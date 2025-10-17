#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Selenium获取Twitter推文（无需API）
通过浏览器自动化抓取Twitter公开推文
"""

import sys
import json
import time
import argparse
from datetime import datetime
import os
import re

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ 请先安装selenium: pip install selenium", file=sys.stderr)
    sys.exit(1)


def setup_driver(headless=True):
    """配置并启动Chrome浏览器"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')  # 无头模式
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
    chrome_options.add_argument('--lang=en-US')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ 启动浏览器失败: {e}", file=sys.stderr)
        print("请确保已安装Chrome浏览器", file=sys.stderr)
        sys.exit(1)


def login_twitter(driver, username=None, password=None):
    """登录Twitter（可选）"""
    if not username or not password:
        return False
    
    try:
        print("🔐 正在登录Twitter...", file=sys.stderr)
        driver.get("https://twitter.com/i/flow/login")
        time.sleep(8)
        
        # 输入用户名/邮箱并按Enter
        try:
            username_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            username_input.clear()
            username_input.send_keys(username)
            username_input.send_keys(Keys.ENTER)
            print("✓ 已输入用户名并提交", file=sys.stderr)
            time.sleep(5)
        except Exception as e:
            print(f"⚠️  输入用户名失败: {e}", file=sys.stderr)
            raise
        
        # 检查是否需要额外验证（邮箱/电话）
        time.sleep(3)
        try:
            # 检查是否有额外输入框（邮箱验证等）
            extra_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]')
            if extra_inputs:
                print("⚠️  检测到额外验证步骤，可能需要输入邮箱或电话", file=sys.stderr)
                # 尝试输入用户名的邮箱部分
                extra_inputs[0].send_keys(username)
                extra_inputs[0].send_keys(Keys.ENTER)
                time.sleep(5)
        except:
            pass
        
        # 输入密码并按Enter
        try:
            password_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            password_input.clear()
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)
            print("✓ 已输入密码并提交", file=sys.stderr)
            time.sleep(10)
        except Exception as e:
            print(f"⚠️  输入密码失败: {e}", file=sys.stderr)
            # 尝试其他密码输入框
            try:
                password_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
                if password_inputs:
                    password_inputs[0].clear()
                    password_inputs[0].send_keys(password)
                    password_inputs[0].send_keys(Keys.ENTER)
                    print("✓ 已输入密码（备用方式）", file=sys.stderr)
                    time.sleep(10)
                else:
                    raise
            except:
                raise
        
        # 检查是否登录成功
        time.sleep(5)
        current_url = driver.current_url
        if 'home' in current_url or 'i/flow' not in current_url:
            print("✅ 登录成功", file=sys.stderr)
            return True
        else:
            print("⚠️  登录可能失败，继续尝试...", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"⚠️  登录失败: {e}", file=sys.stderr)
        print("继续以未登录状态抓取（可能只能获取部分推文）", file=sys.stderr)
        return False


def load_cookies(driver, cookie_file='config/twitter_cookies.json'):
    """加载保存的cookies"""
    try:
        if not os.path.exists(cookie_file):
            return False
        
        print(f"🍪 加载cookies: {cookie_file}", file=sys.stderr)
        
        # 先访问Twitter主页（必须先访问才能添加cookies）
        driver.get("https://twitter.com")
        time.sleep(3)
        
        with open(cookie_file, 'r') as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except:
                pass
        
        print(f"✅ 已加载 {len(cookies)} 个cookie", file=sys.stderr)
        return True
    except Exception as e:
        print(f"⚠️  加载cookies失败: {e}", file=sys.stderr)
        return False


def scrape_tweets(username, num_tweets=10, twitter_user=None, twitter_pass=None, use_cookies=True):
    """
    使用Selenium抓取Twitter推文
    """
    print(f"🐦 正在获取 @{username} 的推文...", file=sys.stderr)
    print("🌐 启动浏览器...", file=sys.stderr)
    
    driver = setup_driver()
    tweets = []
    logged_in = False
    
    try:
        # 优先尝试使用保存的cookies
        if use_cookies:
            logged_in = load_cookies(driver)
        
        # 如果cookies失败且提供了登录信息，尝试登录
        if not logged_in and twitter_user and twitter_pass:
            logged_in = login_twitter(driver, twitter_user, twitter_pass)
        
        if not logged_in:
            print("⚠️  未登录状态访问（可能受限）", file=sys.stderr)
            print("💡 提示：运行 'python3 scripts/twitter_save_cookies.py' 手动登录并保存cookies", file=sys.stderr)
        
        # 访问用户主页
        url = f"https://twitter.com/{username}"
        print(f"📱 访问: {url}", file=sys.stderr)
        driver.get(url)
        
        # 等待页面加载
        print("⏳ 等待页面加载...", file=sys.stderr)
        time.sleep(8)
        
        # 检查页面标题和状态
        page_title = driver.title
        print(f"📄 页面标题: {page_title}", file=sys.stderr)
        
        # 检查是否有"账号被暂停"等提示
        try:
            body_text = driver.find_element(By.TAG_NAME, 'body').text
            if '账号被暂停' in body_text or 'suspended' in body_text.lower() or 'Account suspended' in body_text:
                print(f"⚠️  账号可能被暂停或限制", file=sys.stderr)
        except:
            pass
        
        # 滚动页面加载更多推文
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 50  # 最多滚动50次
        no_new_content_count = 0  # 连续无新内容的次数
        
        while len(tweets) < num_tweets and scroll_attempts < max_scrolls:
            # 查找推文元素
            tweet_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            
            print(f"📊 第{scroll_attempts+1}次扫描，找到 {len(tweet_elements)} 个推文元素，已获取 {len(tweets)} 条推文", file=sys.stderr)
            
            previous_count = len(tweets)
            
            # 提取推文数据
            for element in tweet_elements:
                if len(tweets) >= num_tweets:
                    break
                
                try:
                    # 提取推文文本
                    text_element = element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                    text = text_element.text if text_element else ''
                    
                    # 提取时间
                    try:
                        time_element = element.find_element(By.TAG_NAME, 'time')
                        created_at = time_element.get_attribute('datetime')
                    except:
                        created_at = ''
                    
                    # 提取链接
                    try:
                        link_elements = element.find_elements(By.CSS_SELECTOR, 'a[href*="/status/"]')
                        tweet_url = ''
                        for link in link_elements:
                            href = link.get_attribute('href')
                            if href and '/status/' in href and username.lower() in href.lower():
                                tweet_url = href
                                break
                    except:
                        tweet_url = ''
                    
                    # 提取互动数据
                    metrics = {
                        'replies': 0,
                        'retweets': 0,
                        'likes': 0,
                        'views': 0
                    }
                    
                    try:
                        # 回复数
                        reply_elements = element.find_elements(By.CSS_SELECTOR, '[data-testid="reply"]')
                        if reply_elements:
                            reply_text = reply_elements[0].text
                            reply_match = re.search(r'(\d+)', reply_text.replace(',', ''))
                            if reply_match:
                                metrics['replies'] = int(reply_match.group(1))
                        
                        # 转推数
                        retweet_elements = element.find_elements(By.CSS_SELECTOR, '[data-testid="retweet"]')
                        if retweet_elements:
                            retweet_text = retweet_elements[0].text
                            retweet_match = re.search(r'(\d+)', retweet_text.replace(',', ''))
                            if retweet_match:
                                metrics['retweets'] = int(retweet_match.group(1))
                        
                        # 点赞数
                        like_elements = element.find_elements(By.CSS_SELECTOR, '[data-testid="like"]')
                        if like_elements:
                            like_text = like_elements[0].text
                            like_match = re.search(r'(\d+)', like_text.replace(',', ''))
                            if like_match:
                                metrics['likes'] = int(like_match.group(1))
                    except:
                        pass
                    
                    # 检查是否已存在（去重）
                    tweet_id = tweet_url.split('/status/')[-1].split('?')[0] if tweet_url else ''
                    
                    if tweet_id and not any(t.get('id') == tweet_id for t in tweets):
                        tweet_data = {
                            'id': tweet_id,
                            'text': text,
                            'created_at': created_at,
                            'url': tweet_url,
                            'metrics': metrics
                        }
                        tweets.append(tweet_data)
                        print(f"  ✓ 推文 {len(tweets)}: {text[:50]}...", file=sys.stderr)
                
                except Exception as e:
                    continue
            
            # 检查是否有新推文
            if len(tweets) == previous_count:
                no_new_content_count += 1
                if no_new_content_count >= 3:
                    print(f"⚠️  连续3次未获取到新推文，停止抓取", file=sys.stderr)
                    break
            else:
                no_new_content_count = 0
            
            # 滚动加载更多
            if len(tweets) < num_tweets:
                # 滚动到底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)  # 增加等待时间让推文加载
                
                # 再向上滚动一点，再向下滚动（触发加载）
                driver.execute_script("window.scrollBy(0, -500);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                
                # 如果高度没变，说明可能到底了，但再试一次
                if new_height == last_height:
                    # 强制滚动更多
                    for _ in range(3):
                        driver.execute_script("window.scrollBy(0, 1000);")
                        time.sleep(2)
                    
                    final_height = driver.execute_script("return document.body.scrollHeight")
                    if final_height == last_height:
                        if no_new_content_count >= 2:
                            print(f"⚠️  页面无法加载更多内容", file=sys.stderr)
                            break
                    else:
                        last_height = final_height
                else:
                    last_height = new_height
                
                scroll_attempts += 1
        
        print(f"\n✅ 成功获取 {len(tweets)} 条推文", file=sys.stderr)
        return tweets
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return tweets
    
    finally:
        driver.quit()
        print("🔒 浏览器已关闭", file=sys.stderr)


def save_to_markdown(username, tweets, output_file):
    """保存推文到Markdown格式"""
    lines = [
        f"# 🐦 @{username} 的推文\n",
        f"📅 获取时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n",
        f"📊 推文数量：{len(tweets)} 条\n",
        f"🔧 获取方式：Selenium浏览器自动化\n",
        "---\n",
    ]
    
    for i, tweet in enumerate(tweets, 1):
        created_at = tweet.get('created_at', '未知时间')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        text = tweet.get('text', '')
        url = tweet.get('url', '')
        metrics = tweet.get('metrics', {})
        
        lines.append(f"\n## {i}. {created_at}\n")
        lines.append(f"{text}\n")
        
        # 统计信息
        stats_parts = []
        if metrics.get('likes'):
            stats_parts.append(f"❤️ {metrics['likes']:,} 点赞")
        if metrics.get('retweets'):
            stats_parts.append(f"🔄 {metrics['retweets']:,} 转推")
        if metrics.get('replies'):
            stats_parts.append(f"💬 {metrics['replies']:,} 回复")
        if metrics.get('views'):
            stats_parts.append(f"👁️ {metrics['views']:,} 浏览")
        
        if stats_parts:
            lines.append("\n**互动数据**: " + " | ".join(stats_parts) + "\n")
        
        if url:
            lines.append(f"\n🔗 [查看原推文]({url})\n")
        
        lines.append("\n---\n")
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(lines))
    
    print(f"✅ Markdown已保存到: {output_file}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Twitter推文抓取工具（Selenium版）')
    parser.add_argument('username', help='Twitter用户名（不含@符号）')
    parser.add_argument('-n', '--num', type=int, default=10,
                       help='要获取的推文数量（默认：10）')
    parser.add_argument('-o', '--output', 
                       help='输出Markdown文件路径')
    parser.add_argument('--login-user',
                       help='Twitter登录用户名（可选，登录后可获取完整推文）')
    parser.add_argument('--login-pass',
                       help='Twitter登录密码（可选）')
    parser.add_argument('--login-config', default='config/twitter_login.json',
                       help='登录配置文件（默认：config/twitter_login.json）')
    
    args = parser.parse_args()
    
    # 获取登录信息
    login_user = args.login_user
    login_pass = args.login_pass
    
    # 如果没有直接提供登录信息，尝试从配置文件读取
    if not login_user and os.path.exists(args.login_config):
        try:
            with open(args.login_config, 'r') as f:
                login_config = json.load(f)
                login_user = login_config.get('username')
                login_pass = login_config.get('password')
                if login_user:
                    print(f"📋 从配置文件读取登录信息: {login_user}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  读取登录配置失败: {e}", file=sys.stderr)
    
    # 获取推文
    tweets = scrape_tweets(args.username, args.num, login_user, login_pass)
    
    if not tweets:
        print("❌ 未能获取到推文", file=sys.stderr)
        sys.exit(1)
    
    # 确定输出路径
    if args.output:
        output_file = args.output
    else:
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'{args.username}_{timestamp}.md')
    
    # 保存为Markdown
    save_to_markdown(args.username, tweets, output_file)
    
    # 同时保存JSON
    json_file = output_file.replace('.md', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'username': args.username,
            'fetch_time': datetime.now().isoformat(),
            'count': len(tweets),
            'tweets': tweets
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON已保存到: {json_file}", file=sys.stderr)
    
    print(f"\n🎉 完成！共获取 {len(tweets)} 条推文", file=sys.stderr)


if __name__ == '__main__':
    main()

