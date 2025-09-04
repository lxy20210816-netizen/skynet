#!/usr/bin/env python
# coding:utf-8

import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from configs.rss_config import chinadigitaltimes_rss_config


class CDTNewsRSSFetcher:
    def __init__(self, rss_url):
        self.rss_url = rss_url
        self.max_articles = 50
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.feed = None
        self.articles = []

    def fetch_rss(self):
        """抓取并解析 RSS"""
        resp = requests.get(self.rss_url, headers=self.headers, timeout=15)
        self.feed = feedparser.parse(resp.content)

        print("feed 标题:", self.feed.feed.get("title", "无"))
        print("共抓到:", len(self.feed.entries), "条新闻")

    def fetch_article_content(self, link):
        """抓取单篇新闻正文"""
        try:
            page = requests.get(link, headers=self.headers, timeout=15)
            soup = BeautifulSoup(page.content, "html.parser")

            # CDT 正文区域
            article_div = soup.find("div", class_="post-content")
            if not article_div:
                return "(未找到正文)"

            paragraphs = [p.get_text(strip=True) for p in article_div.find_all("p")]
            return "\n".join(p for p in paragraphs if p)
        except Exception as e:
            return f"(抓取正文失败: {e})"

    def parse_articles(self):
        """解析 RSS 里的文章"""
        if not self.feed:
            print("请先调用 fetch_rss()")
            return

        for entry in self.feed.entries[:self.max_articles]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))

            # 发布时间处理
            published = entry.get("published", "")
            if "published_parsed" in entry and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")

            content = self.fetch_article_content(link)

            article = {
                "title": title,
                "link": link,
                "summary": summary,
                "published": published,
                "content": content
            }
            self.articles.append(article)

    def run(self):
        """完整流程"""
        self.fetch_rss()
        self.parse_articles()
        return self.articles


if __name__ == "__main__":
    # 中国数字时代 RSS 示例
    rss_url = chinadigitaltimes_rss_config["feed"]
    fetcher = CDTNewsRSSFetcher(rss_url)
    articles = fetcher.run()
    for i, art in enumerate(articles, 1):
        print(f"{i}. {art['title']} ({art['published']})")
        print(f"链接: {art['link']}")
        print(f"摘要: {art['summary'][:60]}...")
        print(f"正文: {art['content'][:100]}...")
        print("=" * 80)
