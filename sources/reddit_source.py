#!/usr/bin/env python
# coding:utf-8

import requests
import feedparser
from datetime import datetime

class RedditRSSFetcher:
    def __init__(self, subreddit):
        # Reddit RSS URL
        self.rss_url = f"https://www.reddit.com/r/{subreddit}/.rss"
        self.max_posts = 500
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.feed = None
        self.posts = []

    def fetch_rss(self):
        """抓取并解析 RSS"""
        resp = requests.get(self.rss_url, headers=self.headers, timeout=10)
        self.feed = feedparser.parse(resp.content)

        print("subreddit 标题:", self.feed.feed.get("title", "无"))
        print("共抓到:", len(self.feed.entries), "条帖子")

    def parse_posts(self):
        """解析 RSS 里的帖子"""
        if not self.feed:
            print("请先调用 fetch_rss()")
            return

        for entry in self.feed.entries[:self.max_posts]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))

            # 发布时间
            published = entry.get("published", "")
            if "published_parsed" in entry and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")

            post = {
                "title": title,
                "link": link,
                "summary": summary,
                "published": published
            }
            self.posts.append(post)

    def run(self):
        """完整流程"""
        self.fetch_rss()
        self.parse_posts()
        return self.posts


if __name__ == "__main__":
    subreddit = "hamiltonwatches"  # 目标子版块
    fetcher = RedditRSSFetcher(subreddit)
    posts = fetcher.run()
    for p in posts:
        print(p)
