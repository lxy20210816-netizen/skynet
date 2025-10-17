#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看回复类型发文的完整结构"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--lang=zh-CN,zh;q=0.9')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    return driver

def main():
    driver = setup_driver()
    
    try:
        url = "https://xueqiu.com/u/1247347556"
        print(f"访问: {url}", file=sys.stderr)
        driver.get(url)
        
        # 等待WAF验证
        time.sleep(15)
        
        # 获取所有article
        articles = driver.find_elements(By.TAG_NAME, "article")
        print(f"\n找到 {len(articles)} 个article\n", file=sys.stderr)
        
        # 查看第7个article（包含"回复@xlli-777"）
        article = articles[6]
        
        print("="*80, file=sys.stderr)
        print("Article #7 的完整HTML:", file=sys.stderr)
        print("="*80, file=sys.stderr)
        html = article.get_attribute('outerHTML')
        print(html[:2000], file=sys.stderr)
        print("\n...(省略部分)...\n", file=sys.stderr)
        
        # 查找可能包含引用内容的元素
        print("\n查找引用内容的元素:", file=sys.stderr)
        print("-"*80, file=sys.stderr)
        
        # 尝试各种可能的选择器
        selectors = [
            '.timeline__item__forward',
            '.forward',
            '.quote',
            '.retweet',
            '.reference',
            'blockquote',
            '.timeline__item__main > div',
            '[class*="forward"]',
            '[class*="quote"]'
        ]
        
        for selector in selectors:
            try:
                elems = article.find_elements(By.CSS_SELECTOR, selector)
                if elems:
                    print(f"\n找到 {len(elems)} 个 '{selector}' 元素:", file=sys.stderr)
                    for i, elem in enumerate(elems[:2]):
                        text = elem.get_attribute('innerText') or elem.get_attribute('textContent')
                        if text:
                            text = text.strip()[:200]
                            print(f"  元素 {i+1}: {text}...", file=sys.stderr)
            except:
                pass
        
        # 获取article的所有文本内容
        print(f"\n\nArticle完整文本:", file=sys.stderr)
        print("-"*80, file=sys.stderr)
        full_text = article.get_attribute('innerText') or article.text
        print(full_text[:800], file=sys.stderr)
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()

