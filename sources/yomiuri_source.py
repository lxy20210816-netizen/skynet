#!/usr/bin/env python
# coding:utf-8

import asyncio
from playwright.async_api import async_playwright
from configs.url_config import yomiuri_url_config


class YomiuriPlaywrightFetcher:
    def __init__(self, url=yomiuri_url_config["ranking"]):
        self.url = url
        self.max_articles = 50
        self.articles = []

    async def _fetch_page(self):
        """用 Playwright 打开读卖新闻排行榜页面"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self.url, timeout=20000)
            await page.wait_for_selector("section", timeout=10000)
            items = await page.query_selector_all("section ul li a")
            await self._parse_articles(items, browser)

    async def _parse_articles(self, items, browser):
        """解析排行榜里的文章信息"""
        for item in items[:self.max_articles]:
            title = await item.inner_text()
            link = await item.get_attribute("href")
            if link and link.startswith("/"):
                link = "https://www.yomiuri.co.jp" + link
            if len(title.strip()) > 10:
                self.articles.append({
                    "title": title.strip(),
                    "link": link
                })
        await browser.close()

    def run(self):
        """完整流程"""
        asyncio.run(self._fetch_page())
        return self.articles


if __name__ == "__main__":
    fetcher = YomiuriPlaywrightFetcher()
    articles = fetcher.run()
    for i, art in enumerate(articles, 1):
        print(f"{i}. {art['title']} ({art['link']})")
