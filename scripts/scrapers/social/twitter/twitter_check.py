#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Twitter推文是否存在
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 设置Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)

# 访问特定推文
url = "https://x.com/realDonaldTrump"
print(f"访问: {url}")
driver.get(url)
time.sleep(10)

# 检查页面内容
print(f"\n页面标题: {driver.title}")

# 查找所有推文
tweets = driver.find_elements(By.CSS_SELECTOR, 'article')
print(f"\n找到 {len(tweets)} 个article元素")

# 查找推文卡片
tweet_cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
print(f"找到 {len(tweet_cards)} 个推文卡片")

# 获取页面源码片段
body = driver.find_element(By.TAG_NAME, 'body')
print(f"\n页面文本前500字符:\n{body.text[:500]}")

driver.quit()

