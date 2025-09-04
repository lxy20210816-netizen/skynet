#!/usr/bin/env python
# coding:utf-8

import asyncio
from playwright.async_api import async_playwright


class YomiuriPlaywrightFetcher:
    def __init__(self, url="https://www.yomiuri.co.jp/ranking/"):
        self.url = url

    async def fetch_hot_list(self, max_articles=10):
        articles = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self.url, timeout=20000)

            # 等待ランキング区域出现
            await page.wait_for_selector("section", timeout=10000)

            # 抓取総合ランキング的文章链接
            items = await page.query_selector_all("section ul li a")
            for item in items[:max_articles]:
                title = await item.inner_text()
                link = await item.get_attribute("href")
                if link and link.startswith("/"):
                    link = "https://www.yomiuri.co.jp" + link
                articles.append({
                    "title": title.strip(),
                    "link": link
                })

            await browser.close()
        return articles

    def run(self):
        return asyncio.run(self.fetch_hot_list())


if __name__ == "__main__":
    fetcher = YomiuriPlaywrightFetcher()
    articles = fetcher.run()
    for i, art in enumerate(articles, 1):
        print(f"{i}. {art['title']} ({art['link']})")
