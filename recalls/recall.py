#!/usr/bin/env python
# coding:utf-8
from sources.asahi_source import AsahiRSSFetcher
from sources.nhk_source import NHKNewsRSSFetcher
from configs.rss_config import *


class Recall:
    def __init__(self):
        self.asahi_newsheadlines_rss_fetcher = AsahiRSSFetcher(asahi_rss_config["newsheadlines"])
        self.nhk_cat0_rss_fetcher = NHKNewsRSSFetcher(nhk_rss_config["cat0"])

    def fetch_all(self):
        asahi_newsheadlines_articles = self.asahi_newsheadlines_rss_fetcher.run()
        nhk_cat0_articles = self.nhk_cat0_rss_fetcher.run()

        return asahi_newsheadlines_articles + nhk_cat0_articles

if __name__ == "__main__":
    recall = Recall()
    res = recall.fetch_all()
    print(res)