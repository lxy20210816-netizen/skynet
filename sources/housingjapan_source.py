#!/usr/bin/env python
#coding:utf-8

import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

from configs.rss_config import housingjapan_rss_config


class HousingjapanRSSFetcher:
    def __init__(self, rss_url):
        self.rss_url = rss_url
        self.max_articles = 10
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.feed = None
        self.articles = []

    def fetch_feed(self):
        """拉取 RSS 并解析"""
        resp = requests.get(self.rss_url, headers=self.headers, timeout=10)
        self.feed = feedparser.parse(resp.content)
        print("feed 标题:", self.feed.feed.get("title", "无"))
        print("共抓到:", len(self.feed.entries), "条新闻")

    def parse_summary(self, entry):
        """解析摘要（去掉 HTML 标签）"""
        summary = entry.get("summary", "")
        soup = BeautifulSoup(summary, "html.parser")
        return soup.get_text().strip()

    def fetch_article_content(self, url):
        """抓取文章正文"""
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(resp.content, "html.parser")

            # HousingJapan 的正文大概率在 <div class="content"> 或 <article>
            content_div = soup.find("div", class_="content") or soup.find("article")

            if content_div:
                return "\n".join(p.get_text(strip=True) for p in content_div.find_all("p")) \
                       or content_div.get_text().strip()
            return "(未找到正文)"
        except Exception as e:
            return f"(抓取正文失败: {e})"

    def parse_articles(self):
        """解析文章列表"""
        if not self.feed:
            print("请先调用 fetch_feed()")
            return

        for entry in self.feed.entries[:self.max_articles]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = self.parse_summary(entry)

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
        self.fetch_feed()
        self.parse_articles()
        return self.articles


if __name__ == "__main__":
    fetcher = HousingjapanRSSFetcher(housingjapan_rss_config["feed"])
    articles = fetcher.run()
    print(articles)
