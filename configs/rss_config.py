#!/usr/bin/env python
#coding:utf-8

asahi_rss_config = {
    "newsheadlines": "https://www.asahi.com/rss/asahi/newsheadlines.rdf",   # 全ジャンル（速報）,每次大概40个
}

nhk_rss_config = {
    "cat0": "https://www3.nhk.or.jp/rss/news/cat0.xml",   # 总合（头条），每次就7个
}

housingjapan_rss_config = {
    "feed": "https://housingjapan.com/blog/feed",   # 最主要的，好像也就这一个，每次就10个
}

wallstreetcn_rss_config = {
    "hot": "https://rss.injahow.cn/wallstreetcn/hot"    # 最热文章，每次大概100个
}

wsj_rss_config = {
    "world": "https://feeds.a.dj.com/rss/RSSWorldNews.xml", # 世界新闻，每次大概20个
    #"us": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
    #"markets": "https://feeds.a.dj.com/rss/WSJcomMarkets.xml",
    #"tech": "https://feeds.a.dj.com/rss/RSSWSJD.xml"
}

chinadigitaltimes_rss_config = {
    "feed": "https://chinadigitaltimes.net/chinese/feed/"   # 最主要的，好像也就这一个，每次就7个
}

youtube_rss_config = {
    "xiao_lin_shuo": "https://www.youtube.com/feeds/videos.xml?channel_id=UCilwQlk62k1z7aUEZPOB6yw" # 小Lin说,每次更新最近15个
}