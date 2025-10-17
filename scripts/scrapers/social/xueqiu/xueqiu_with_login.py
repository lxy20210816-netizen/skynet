#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雪球爬虫 - 支持登录版本
需要登录后才能查看用户发文
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
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ 请先安装selenium: pip install selenium", file=sys.stderr)
    sys.exit(1)


# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
COOKIES_FILE = os.path.join(CONFIG_DIR, 'xueqiu_cookies.json')
LOGIN_CONFIG = os.path.join(CONFIG_DIR, 'xueqiu_login.json')

# 段永平的雪球ID
DEFAULT_USER_ID = "9528875558"


def setup_driver(headless=True):
    """配置并启动Chrome浏览器"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # 禁用自动化检测
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 添加语言设置
    chrome_options.add_argument('--lang=zh-CN')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # 执行CDP命令来隐藏webdriver属性
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        return driver
    except Exception as e:
        print(f"❌ 启动浏览器失败: {e}", file=sys.stderr)
        sys.exit(1)


def load_cookies(driver):
    """从文件加载cookies"""
    if not os.path.exists(COOKIES_FILE):
        return False
    
    try:
        with open(COOKIES_FILE, 'r') as f:
            cookies = json.load(f)
        
        # 先访问雪球首页
        driver.get("https://xueqiu.com")
        time.sleep(2)
        
        # 添加cookies
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except:
                pass
        
        print("✅ 已加载保存的cookies", file=sys.stderr)
        return True
    
    except Exception as e:
        print(f"⚠️  加载cookies失败: {e}", file=sys.stderr)
        return False


def save_cookies(driver):
    """保存cookies到文件"""
    try:
        cookies = driver.get_cookies()
        
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(COOKIES_FILE, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"✅ Cookies已保存到: {COOKIES_FILE}", file=sys.stderr)
        return True
    
    except Exception as e:
        print(f"❌ 保存cookies失败: {e}", file=sys.stderr)
        return False


def login_xueqiu(driver, phone=None, password=None):
    """
    登录雪球
    
    Args:
        driver: Selenium WebDriver
        phone: 手机号（可选，从配置文件读取）
        password: 密码（可选，从配置文件读取）
    
    Returns:
        bool: 登录是否成功
    """
    # 如果没有提供账号密码，尝试从配置文件读取
    if not phone or not password:
        if os.path.exists(LOGIN_CONFIG):
            try:
                with open(LOGIN_CONFIG, 'r') as f:
                    config = json.load(f)
                    phone = config.get('phone')
                    password = config.get('password')
            except:
                pass
    
    if not phone or not password:
        print("❌ 未提供登录信息", file=sys.stderr)
        print(f"💡 请创建配置文件: {LOGIN_CONFIG}", file=sys.stderr)
        print('   内容格式: {"phone": "你的手机号", "password": "你的密码"}', file=sys.stderr)
        return False
    
    try:
        print("🔐 正在登录雪球...", file=sys.stderr)
        
        # 访问登录页面
        driver.get("https://xueqiu.com")
        time.sleep(3)
        
        # 点击登录按钮
        try:
            login_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '登录')]"))
            )
            login_btn.click()
            print("✓ 点击登录按钮", file=sys.stderr)
            time.sleep(3)
        except Exception as e:
            print(f"⚠️  查找登录按钮失败: {e}", file=sys.stderr)
            # 可能已经在登录页面
        
        # 切换到手机号登录
        try:
            phone_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '手机号')]"))
            )
            phone_tab.click()
            print("✓ 切换到手机号登录", file=sys.stderr)
            time.sleep(2)
        except:
            print("⚠️  可能已经是手机号登录界面", file=sys.stderr)
        
        # 输入手机号
        try:
            phone_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='手机号']"))
            )
            phone_input.clear()
            phone_input.send_keys(phone)
            print("✓ 已输入手机号", file=sys.stderr)
            time.sleep(1)
        except Exception as e:
            print(f"❌ 输入手机号失败: {e}", file=sys.stderr)
            return False
        
        # 输入密码
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.clear()
            password_input.send_keys(password)
            print("✓ 已输入密码", file=sys.stderr)
            time.sleep(1)
        except Exception as e:
            print(f"❌ 输入密码失败: {e}", file=sys.stderr)
            return False
        
        # 点击登录按钮
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_btn.click()
            print("✓ 点击登录", file=sys.stderr)
            time.sleep(5)
        except Exception as e:
            print(f"❌ 点击登录按钮失败: {e}", file=sys.stderr)
            return False
        
        # 检查是否需要验证码
        time.sleep(3)
        try:
            # 检查是否有验证码元素
            captcha = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='验证码']")
            if captcha:
                print("⚠️  需要输入验证码，请在浏览器中手动完成", file=sys.stderr)
                print("等待60秒供手动操作...", file=sys.stderr)
                time.sleep(60)
        except:
            pass
        
        # 验证登录是否成功
        time.sleep(3)
        current_url = driver.current_url
        
        if "login" not in current_url.lower():
            print("✅ 登录成功！", file=sys.stderr)
            # 保存cookies
            save_cookies(driver)
            return True
        else:
            print("❌ 登录失败，请检查账号密码", file=sys.stderr)
            return False
    
    except Exception as e:
        print(f"❌ 登录过程出错: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def get_user_posts_with_scroll(driver, user_id, max_posts=20):
    """
    通过滚动获取用户发文（登录后版本）
    """
    posts = []
    
    try:
        # 访问用户主页
        url = f"https://xueqiu.com/u/{user_id}"
        print(f"📖 正在访问用户主页: {url}", file=sys.stderr)
        driver.get(url)
        time.sleep(5)
        
        # 获取用户名
        try:
            username_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-name, .user-name"))
            )
            username = username_elem.text
            print(f"👤 用户名: {username}", file=sys.stderr)
        except:
            username = f"User_{user_id}"
            print(f"⚠️  无法获取用户名，使用默认名称", file=sys.stderr)
        
        # 滚动加载发文
        scroll_count = 0
        max_scrolls = 15
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while scroll_count < max_scrolls and len(posts) < max_posts:
            # 查找发文卡片 - 尝试多个选择器
            post_selectors = [
                "article.status-card",
                ".timeline-item",
                ".status-item",
                "div[data-id]",  # 发文通常有data-id属性
            ]
            
            post_elements = []
            for selector in post_selectors:
                post_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if post_elements:
                    print(f"✓ 使用选择器 '{selector}' 找到 {len(post_elements)} 个元素", file=sys.stderr)
                    break
            
            if not post_elements:
                print(f"⚠️  第 {scroll_count + 1} 次滚动: 未找到发文元素", file=sys.stderr)
            else:
                print(f"📊 第 {scroll_count + 1} 次滚动: 找到 {len(post_elements)} 条发文", file=sys.stderr)
                
                for elem in post_elements:
                    if len(posts) >= max_posts:
                        break
                    
                    try:
                        post_data = extract_post_from_element(elem, user_id, username)
                        
                        if post_data and post_data.get('id'):
                            # 避免重复
                            if not any(p.get('id') == post_data.get('id') for p in posts):
                                posts.append(post_data)
                                title = post_data.get('title', '')[:40]
                                print(f"✅ [{len(posts)}/{max_posts}] {title}...", file=sys.stderr)
                    except Exception as e:
                        continue
            
            # 滚动到底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 检查是否还能加载更多
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("📭 已到页面底部，无更多内容", file=sys.stderr)
                break
            last_height = new_height
            scroll_count += 1
        
        print(f"\n✅ 共获取到 {len(posts)} 条发文", file=sys.stderr)
        return posts
    
    except Exception as e:
        print(f"❌ 获取发文失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return posts


def extract_post_from_element(elem, user_id, username):
    """从页面元素提取发文数据"""
    post_data = {
        'user_id': user_id,
        'username': username,
        'scraped_at': datetime.now().isoformat()
    }
    
    try:
        # 提取ID和URL
        post_id = elem.get_attribute('data-id')
        if post_id:
            post_data['id'] = post_id
            post_data['url'] = f"https://xueqiu.com/{user_id}/{post_id}"
    except:
        pass
    
    try:
        # 提取内容
        text_elem = elem.find_element(By.CSS_SELECTOR, ".status-content, .timeline-content, .text")
        text = text_elem.text.strip()
        post_data['title'] = text[:100] if len(text) > 100 else text
        post_data['content'] = text
    except:
        pass
    
    try:
        # 提取时间
        time_elem = elem.find_element(By.CSS_SELECTOR, ".status-time, .time, time")
        post_data['published_at'] = time_elem.text.strip()
    except:
        pass
    
    try:
        # 提取互动数据
        action_items = elem.find_elements(By.CSS_SELECTOR, ".action-item, .status-action-item")
        for item in action_items:
            text = item.text.strip()
            if '赞' in text or '点赞' in text:
                post_data['likes'] = text
            elif '评论' in text:
                post_data['comments'] = text
            elif '转发' in text:
                post_data['retweets'] = text
    except:
        pass
    
    return post_data


def save_to_file(posts, output_file):
    """保存到文件"""
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON已保存到: {output_file}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}", file=sys.stderr)
        return False


def format_to_markdown(posts, username=""):
    """格式化为Markdown"""
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
        
        if post.get('content') and post.get('content') != post.get('title'):
            lines.append(f"\n{post['content']}\n")
        
        stats = []
        if post.get('likes'):
            stats.append(f"👍 {post['likes']}")
        if post.get('comments'):
            stats.append(f"💬 {post['comments']}")
        if post.get('retweets'):
            stats.append(f"🔄 {post['retweets']}")
        
        if stats:
            lines.append(f"\n*{' | '.join(stats)}*\n")
        
        lines.append("\n---\n")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='雪球爬虫（支持登录）')
    parser.add_argument('--user-id', type=str, default=DEFAULT_USER_ID,
                        help=f'雪球用户ID (默认: {DEFAULT_USER_ID})')
    parser.add_argument('--max-posts', type=int, default=20,
                        help='最多获取的发文数量')
    parser.add_argument('--output', type=str, default='../output/xueqiu_posts.json',
                        help='输出文件路径')
    parser.add_argument('--format', type=str, choices=['json', 'markdown', 'both'], default='both',
                        help='输出格式')
    parser.add_argument('--phone', type=str, help='登录手机号')
    parser.add_argument('--password', type=str, help='登录密码')
    parser.add_argument('--visible', action='store_true', help='显示浏览器')
    parser.add_argument('--force-login', action='store_true', help='强制重新登录')
    
    args = parser.parse_args()
    
    print("=" * 60, file=sys.stderr)
    print("📊 雪球爬虫（支持登录）", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"👤 用户ID: {args.user_id}", file=sys.stderr)
    print(f"📝 最多获取: {args.max_posts}条", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("", file=sys.stderr)
    
    # 启动浏览器
    headless = not args.visible
    driver = setup_driver(headless=headless)
    
    try:
        # 尝试加载cookies
        cookies_loaded = False
        if not args.force_login and os.path.exists(COOKIES_FILE):
            cookies_loaded = load_cookies(driver)
            if cookies_loaded:
                # 验证cookies是否有效
                driver.get("https://xueqiu.com")
                time.sleep(3)
                # 检查是否仍然登录
                if "login" in driver.current_url.lower():
                    print("⚠️  Cookies已失效，需要重新登录", file=sys.stderr)
                    cookies_loaded = False
        
        # 如果cookies无效或强制登录，进行登录
        if not cookies_loaded:
            if not login_xueqiu(driver, args.phone, args.password):
                print("\n💡 提示：", file=sys.stderr)
                print(f"1. 创建登录配置文件: {LOGIN_CONFIG}", file=sys.stderr)
                print('   {"phone": "你的手机号", "password": "你的密码"}', file=sys.stderr)
                print("2. 或使用 --phone 和 --password 参数", file=sys.stderr)
                driver.quit()
                return
        
        # 获取发文
        posts = get_user_posts_with_scroll(driver, args.user_id, args.max_posts)
        
        if not posts:
            print("❌ 没有获取到发文", file=sys.stderr)
            return
        
        username = posts[0].get('username', '') if posts else ''
        
        # 保存数据
        if args.format in ['json', 'both']:
            save_to_file(posts, args.output)
        
        if args.format in ['markdown', 'both']:
            md_file = args.output.replace('.json', '.md')
            md_content = format_to_markdown(posts, username)
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"📝 Markdown已保存到: {md_file}", file=sys.stderr)
        
        # 输出
        if args.format == 'markdown':
            print(format_to_markdown(posts, username))
        else:
            print(json.dumps(posts, ensure_ascii=False, indent=2))
        
        print("\n✅ 抓取完成！", file=sys.stderr)
    
    finally:
        driver.quit()


if __name__ == '__main__':
    main()

