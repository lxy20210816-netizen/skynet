#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雪球用户发文爬虫 - 改进版
增强反检测能力
"""

import sys
import json
import time
import argparse
import os
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("❌ 请先安装selenium: pip install selenium", file=sys.stderr)
    sys.exit(1)


def setup_driver(headless=True):
    """配置浏览器 - 增强反检测"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless=new')
    
    # 基础设置
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # 更真实的User-Agent
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 禁用自动化特征
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 添加更多参数
    chrome_options.add_argument('--lang=zh-CN,zh;q=0.9')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--start-maximized')
    
    # 设置更多prefs
    prefs = {
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
        'profile.default_content_setting_values': {
            'notifications': 2
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 注入JavaScript隐藏webdriver
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });
            window.chrome = {
                runtime: {}
            };
        '''
    })
    
    return driver


def get_user_posts(driver, user_id, max_posts=20):
    """获取用户发文"""
    posts = []
    
    try:
        url = f"https://xueqiu.com/u/{user_id}"
        print(f"📖 访问: {url}", file=sys.stderr)
        
        driver.get(url)
        
        # 等待更长时间让WAF验证完成
        print("⏳ 等待页面加载（15秒）...", file=sys.stderr)
        time.sleep(15)
        
        # 检查是否被WAF拦截
        page_source = driver.page_source
        if '_waf_' in page_source and 'renderData' in page_source:
            print("⚠️  检测到WAF保护，再等待10秒...", file=sys.stderr)
            time.sleep(10)
            driver.refresh()
            time.sleep(10)
        
        # 尝试获取用户名
        username = "未知用户"
        try:
            username_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-name, .user-name, h2.name"))
            )
            username = username_elem.text
            print(f"👤 用户名: {username}", file=sys.stderr)
        except:
            print(f"⚠️  无法获取用户名", file=sys.stderr)
        
        # 滚动加载
        scroll_count = 0
        max_scrolls = 10
        
        while scroll_count < max_scrolls and len(posts) < max_posts:
            # 查找发文 - 尝试所有可能的选择器
            post_elements = []
            selectors = [
                "article",
                "div[class*='status']",
                "div[class*='timeline']",
                "div[class*='card']",
                "li[class*='item']",
                ".timeline__item",
                ".status-item",
                ".card-item"
            ]
            
            for selector in selectors:
                post_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if post_elements:
                    print(f"📊 使用 '{selector}' 找到 {len(post_elements)} 个元素", file=sys.stderr)
                    break
            
            if not post_elements:
                # 尝试通过链接查找
                all_links = driver.find_elements(By.TAG_NAME, "a")
                post_links = [link for link in all_links if link.get_attribute('href') and f'/u/{user_id}/' in link.get_attribute('href')]
                
                if post_links:
                    print(f"📊 通过链接找到 {len(post_links)} 条发文", file=sys.stderr)
                    for link in post_links[:max_posts]:
                        try:
                            post_url = link.get_attribute('href')
                            post_id = post_url.split('/')[-1].split('?')[0]
                            post_text = link.text.strip()
                            
                            post_data = {
                                'id': post_id,
                                'user_id': user_id,
                                'username': username,
                                'url': post_url,
                                'title': post_text[:100] if post_text else '无标题',
                                'content': post_text,
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            if post_data['id'] and not any(p.get('id') == post_data['id'] for p in posts):
                                posts.append(post_data)
                                print(f"✅ [{len(posts)}/{max_posts}] {post_text[:40]}...", file=sys.stderr)
                        except:
                            continue
                    break
            else:
                # 处理找到的元素
                for elem in post_elements:
                    if len(posts) >= max_posts:
                        break
                    
                    try:
                        post_data = extract_post_data(elem, user_id, username)
                        if post_data and post_data.get('id'):
                            if not any(p.get('id') == post_data['id'] for p in posts):
                                posts.append(post_data)
                                print(f"✅ [{len(posts)}/{max_posts}] {post_data.get('title', '')[:40]}...", file=sys.stderr)
                    except:
                        continue
            
            # 滚动
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            scroll_count += 1
        
        print(f"\n✅ 共获取 {len(posts)} 条发文", file=sys.stderr)
        return posts
        
    except Exception as e:
        print(f"❌ 获取失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return posts


def extract_post_data(elem, user_id, username):
    """提取发文数据"""
    post_data = {
        'user_id': user_id,
        'username': username,
        'scraped_at': datetime.now().isoformat()
    }
    
    # 提取链接和ID - 雪球的格式是 /user_id/post_id
    try:
        links = elem.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute('href')
            # 查找格式为 /user_id/数字 的链接
            if href and f'/{user_id}/' in href:
                post_data['url'] = href
                post_data['id'] = href.split('/')[-1].split('?')[0]
                
                # 尝试提取时间
                link_text = link.text.strip()
                if '·' in link_text and ('来自' in link_text or ':' in link_text):
                    post_data['published_at'] = link_text
                break
    except:
        pass
    
    # 提取被引用/转发的原文
    quoted_text = None
    try:
        quote_selectors = [
            'blockquote.timeline__item__forward',
            '.timeline__item__forward',
            'blockquote',
            '.quote',
            '.forward'
        ]
        
        for selector in quote_selectors:
            try:
                quote_elem = elem.find_element(By.CSS_SELECTOR, selector)
                quoted_text = quote_elem.get_attribute('innerText') or quote_elem.get_attribute('textContent')
                if quoted_text and quoted_text.strip():
                    quoted_text = quoted_text.strip()
                    post_data['quoted_text'] = quoted_text
                    break
            except:
                continue
    except:
        pass
    
    # 提取文本内容 - 使用多种方法
    content = None
    
    # 方法1: 尝试通过CSS选择器直接获取内容区域
    try:
        content_selectors = [
            '.content--description',
            '.content',
            '.timeline__item__content',
            '.status-content'
        ]
        
        for selector in content_selectors:
            try:
                content_elem = elem.find_element(By.CSS_SELECTOR, selector)
                # 使用 innerText 或 textContent
                content = content_elem.get_attribute('innerText') or content_elem.get_attribute('textContent')
                if content and content.strip():
                    content = content.strip()
                    # 如果内容中包含了引用文本，去掉引用部分
                    if quoted_text and quoted_text in content:
                        content = content.replace(quoted_text, '').strip()
                    break
            except:
                continue
    except:
        pass
    
    # 方法2: 如果上面没有获取到，尝试用article.text
    if not content:
        try:
            full_text = elem.text.strip()
            if full_text:
                # 如果有引用文本，先去掉
                if quoted_text and quoted_text in full_text:
                    full_text = full_text.replace(quoted_text, '').strip()
                
                # 分割文本，通常第一行或前几行是内容
                lines = full_text.split('\n')
                
                # 跳过用户名和时间行，找到实际内容
                content_lines = []
                for line in lines:
                    line = line.strip()
                    # 跳过用户名、时间、互动数据等
                    if line and line != username and not line.startswith('10-') and \
                       '来自' not in line and '转发' not in line and '讨论' not in line and \
                       '收藏' not in line and not line.isdigit():
                        content_lines.append(line)
                
                content = '\n'.join(content_lines) if content_lines else full_text
        except:
            pass
    
    # 设置title和content
    if content:
        post_data['title'] = content[:100] if len(content) > 100 else content
        post_data['content'] = content
    
    return post_data


def save_to_markdown(posts, output_file):
    """保存为Markdown"""
    username = posts[0].get('username', '未知用户') if posts else '未知用户'
    
    lines = [
        f"# 📊 {username} - 雪球发文\n",
        f"📅 抓取时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n",
        f"📝 发文数量：{len(posts)}条\n",
        "---\n",
    ]
    
    for i, post in enumerate(posts, 1):
        title = post.get('title', '无标题')
        lines.append(f"\n## {i}. {title}\n")
        
        if post.get('published_at'):
            lines.append(f"🕒 **发布时间**: {post['published_at']}\n")
        
        if post.get('url'):
            lines.append(f"🔗 **链接**: {post['url']}\n")
        
        # 如果有被引用的原文，显示出来
        if post.get('quoted_text'):
            lines.append(f"\n### 📌 引用的原文:\n")
            quoted = post['quoted_text'].replace('\n', '\n> ')
            lines.append(f"> {quoted}\n")
        
        if post.get('content') and post.get('content') != title:
            lines.append(f"\n### 💬 回复内容:\n")
            lines.append(f"{post['content']}\n")
        
        lines.append("\n---\n")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='雪球爬虫改进版')
    parser.add_argument('--user-id', type=str, required=True, help='雪球用户ID')
    parser.add_argument('--max-posts', type=int, default=20, help='最多获取的发文数量')
    parser.add_argument('--output', type=str, default='../output/xueqiu.md', help='输出文件')
    parser.add_argument('--visible', action='store_true', help='显示浏览器')
    
    args = parser.parse_args()
    
    print("=" * 60, file=sys.stderr)
    print("📊 雪球爬虫改进版", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"👤 用户ID: {args.user_id}", file=sys.stderr)
    print(f"📝 最多获取: {args.max_posts}条", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("", file=sys.stderr)
    
    driver = setup_driver(headless=not args.visible)
    
    try:
        posts = get_user_posts(driver, args.user_id, args.max_posts)
        
        if posts:
            markdown = save_to_markdown(posts, args.output)
            print(f"\n💾 已保存到: {args.output}", file=sys.stderr)
            print("\n" + markdown)
        else:
            print("❌ 没有获取到发文", file=sys.stderr)
            
    finally:
        driver.quit()


if __name__ == '__main__':
    main()

