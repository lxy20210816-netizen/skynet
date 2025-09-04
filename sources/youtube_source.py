#!/usr/bin/env python
# coding:utf-8

import requests
import feedparser
from datetime import datetime
from configs.rss_config import youtube_rss_config

class YouTubeRSSFetcher:
    def __init__(self, rss_url):
        self.rss_url = rss_url
        self.max_videos = 50
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.feed = None
        self.videos = []

    def fetch_rss(self):
        """抓取并解析 RSS"""
        resp = requests.get(self.rss_url, headers=self.headers, timeout=10)
        self.feed = feedparser.parse(resp.content)

        print("频道标题:", self.feed.feed.get("title", "无"))
        print("共抓到:", len(self.feed.entries), "条视频")

    def parse_videos(self):
        """解析 RSS 里的视频"""
        if not self.feed:
            print("请先调用 fetch_rss()")
            return

        for entry in self.feed.entries[:self.max_videos]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")
            published = entry.get("published", "")

            # 格式化时间
            if "published_parsed" in entry and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")

            video = {
                "title": title,
                "link": link,
                "summary": summary,
                "published": published
            }
            self.videos.append(video)

    def run(self):
        """完整流程"""
        self.fetch_rss()
        self.parse_videos()
        return self.videos


if __name__ == "__main__":
    # 小Lin说 YouTube RSS 链接（需要替换成实际频道ID）
    rss_url = youtube_rss_config["xiao_lin_shuo"]
    fetcher = YouTubeRSSFetcher(rss_url)
    videos = fetcher.run()
    for v in videos:
        print(v)
