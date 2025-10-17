#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找雪球用户ID的辅助工具
通过用户名搜索获取用户ID
"""

import sys
import json
import time
import argparse

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("❌ 请先安装selenium: pip install selenium", file=sys.stderr)
    sys.exit(1)


def setup_driver(headless=False):
    """配置并启动Chrome浏览器"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ 启动浏览器失败: {e}", file=sys.stderr)
        sys.exit(1)


def search_user(driver, username):
    """搜索用户并获取用户ID"""
    try:
        # 访问雪球首页
        print(f"🔍 搜索用户: {username}", file=sys.stderr)
        driver.get("https://xueqiu.com")
        time.sleep(3)
        
        # 找到搜索框
        search_box = driver.find_element(By.CSS_SELECTOR, "input.search__input")
        search_box.clear()
        search_box.send_keys(username)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(5)  # 等待搜索结果
        
        # 点击"用户"标签
        try:
            user_tab = driver.find_element(By.XPATH, "//a[contains(text(), '用户')]")
            user_tab.click()
            time.sleep(3)
        except:
            print("⚠️  未找到用户标签，尝试直接从结果中查找", file=sys.stderr)
        
        # 查找用户卡片
        user_cards = driver.find_elements(By.CSS_SELECTOR, ".user__item")
        
        if not user_cards:
            # 尝试其他选择器
            user_cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/u/']")
        
        print(f"\n找到 {len(user_cards)} 个用户结果:\n", file=sys.stderr)
        
        users_found = []
        for card in user_cards[:10]:  # 只显示前10个结果
            try:
                # 获取用户链接
                user_link = card.get_attribute('href')
                if not user_link or '/u/' not in user_link:
                    continue
                
                # 提取用户ID
                user_id = user_link.split('/u/')[-1].split('?')[0].split('/')[0]
                
                # 获取用户名
                try:
                    username_elem = card.find_element(By.CSS_SELECTOR, ".user__name")
                    display_name = username_elem.text
                except:
                    display_name = "未知"
                
                # 获取简介
                try:
                    bio_elem = card.find_element(By.CSS_SELECTOR, ".user__bio")
                    bio = bio_elem.text
                except:
                    bio = ""
                
                user_info = {
                    'id': user_id,
                    'name': display_name,
                    'bio': bio,
                    'url': f"https://xueqiu.com/u/{user_id}"
                }
                
                users_found.append(user_info)
                
                print(f"👤 {display_name}", file=sys.stderr)
                print(f"   ID: {user_id}", file=sys.stderr)
                print(f"   链接: https://xueqiu.com/u/{user_id}", file=sys.stderr)
                if bio:
                    print(f"   简介: {bio[:50]}...", file=sys.stderr)
                print("", file=sys.stderr)
            
            except Exception as e:
                continue
        
        if not users_found:
            print("❌ 未找到匹配的用户", file=sys.stderr)
            
            # 显示当前页面的URL供调试
            print(f"当前页面: {driver.current_url}", file=sys.stderr)
            
            # 保存截图
            screenshot_path = "/tmp/xueqiu_search_debug.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 已保存截图到: {screenshot_path}", file=sys.stderr)
        
        return users_found
    
    except Exception as e:
        print(f"❌ 搜索失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return []


def main():
    parser = argparse.ArgumentParser(description='查找雪球用户ID')
    parser.add_argument('username', type=str, help='要搜索的用户名')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')
    
    args = parser.parse_args()
    
    print("=" * 60, file=sys.stderr)
    print("🔍 雪球用户ID查找工具", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("", file=sys.stderr)
    
    driver = setup_driver(headless=args.headless)
    
    try:
        users = search_user(driver, args.username)
        
        if users:
            # 输出JSON格式（可以被其他脚本使用）
            print(json.dumps(users, ensure_ascii=False, indent=2))
        
        # 如果找到"大道无形我有型"，特别提示
        for user in users:
            if '大道无形' in user['name'] or '段永平' in user['name']:
                print("\n" + "=" * 60, file=sys.stderr)
                print("✅ 找到段永平的账号！", file=sys.stderr)
                print(f"   用户ID: {user['id']}", file=sys.stderr)
                print(f"   主页: {user['url']}", file=sys.stderr)
                print("=" * 60, file=sys.stderr)
    
    finally:
        driver.quit()


if __name__ == '__main__':
    main()

