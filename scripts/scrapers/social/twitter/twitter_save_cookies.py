#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter手动登录并保存Cookies
运行后会打开浏览器窗口，你手动登录，登录成功后cookies会自动保存
"""

import time
import json
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def save_twitter_cookies():
    """手动登录Twitter并保存cookies"""
    print("=" * 60)
    print("🔐 Twitter手动登录工具")
    print("=" * 60)
    print("\n📝 操作步骤：")
    print("1. 浏览器窗口会自动打开")
    print("2. 请在浏览器中手动登录Twitter")
    print("3. 等待90秒后自动保存cookies\n")
    
    # 启动浏览器（非无头模式）
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🌐 正在打开Twitter登录页面...")
        driver.get("https://twitter.com/i/flow/login")
        
        print("✅ 浏览器已打开")
        print("\n⏰ 请在90秒内完成登录...")
        
        # 倒计时
        for i in range(90, 0, -10):
            print(f"   剩余 {i} 秒...", flush=True)
            time.sleep(10)
        
        print("\n💾 正在保存cookies...")
        
        # 保存cookies
        cookies = driver.get_cookies()
        
        if not cookies:
            print("❌ 未能获取cookies，请确保已成功登录")
            return False
        
        # 保存到文件
        cookie_file = 'config/twitter_cookies.json'
        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"\n✅ Cookies已保存到: {cookie_file}")
        print(f"📊 共保存 {len(cookies)} 个cookie")
        print("\n🎉 完成！以后抓取推文时会自动使用这些cookies")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 保存cookies失败: {e}")
        return False
    
    finally:
        print("\n🔒 关闭浏览器...")
        driver.quit()


if __name__ == '__main__':
    save_twitter_cookies()

