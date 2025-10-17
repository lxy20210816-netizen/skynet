#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
朝日新闻RSS抓取脚本
获取朝日新闻RSS feed并保存为JSON格式
"""

import sys
import json
import os
from datetime import datetime

try:
    import feedparser
except ImportError:
    print("❌ 请先安装feedparser: pip install feedparser", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    print("❌ 请先安装requests: pip install requests", file=sys.stderr)
    sys.exit(1)


# RSS链接
RSS_URL = "https://www.asahi.com/rss/asahi/newsheadlines.rdf"

# 输出目录
OUTPUT_DIR = "/Users/a0000/Desktop/workspace/brain/skynet"


def fetch_rss_feed(url):
    """
    获取RSS feed
    
    Args:
        url: RSS feed的URL
    
    Returns:
        feedparser解析后的对象
    """
    try:
        print(f"📡 正在获取RSS: {url}", file=sys.stderr)
        
        # 使用requests获取内容（可以设置超时和headers）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 使用feedparser解析
        feed = feedparser.parse(response.content)
        
        print(f"✅ 成功获取 {len(feed.entries)} 条新闻", file=sys.stderr)
        return feed
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取RSS失败: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ 解析RSS失败: {e}", file=sys.stderr)
        return None


def parse_date(entry):
    """
    解析日期字符串为标准格式
    
    Args:
        entry: RSS entry对象
    
    Returns:
        格式化的日期字符串 (YYYY-MM-DD HH:MM:SS)
    """
    try:
        # 尝试多个日期字段
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            dt = datetime(*entry.published_parsed[:6])
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            dt = datetime(*entry.updated_parsed[:6])
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif 'published' in entry:
            # 尝试直接解析字符串
            return entry.published
        return ""
    except Exception as e:
        return ""


def convert_to_json_format(feed, start_id=1):
    """
    将RSS feed转换为指定的JSON格式
    
    Args:
        feed: feedparser解析后的feed对象
        start_id: 起始ID
    
    Returns:
        list: JSON格式的新闻列表
    """
    news_list = []
    
    for idx, entry in enumerate(feed.entries, start=start_id):
        news_item = {
            "id": idx,
            "title": entry.get('title', ''),
            "link": entry.get('link', ''),
            "pubDate": parse_date(entry),
            "content": entry.get('description', ''),
            "contentSnippet": entry.get('summary', '')
        }
        news_list.append(news_item)
    
    return news_list


def save_to_json(news_list, output_dir):
    """
    保存新闻列表为JSON文件
    
    Args:
        news_list: 新闻列表
        output_dir: 输出目录
    
    Returns:
        str: 保存的文件路径
    """
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名（当前日期）
        today = datetime.now()
        filename = f"asahi_newsheadlines_{today.strftime('%Y%m%d')}.json"
        filepath = os.path.join(output_dir, filename)
        
        # 保存JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存到: {filepath}", file=sys.stderr)
        print(f"📊 共保存 {len(news_list)} 条新闻", file=sys.stderr)
        
        return filepath
        
    except Exception as e:
        print(f"❌ 保存文件失败: {e}", file=sys.stderr)
        return None


def print_summary(news_list):
    """打印新闻摘要"""
    print("\n" + "="*60, file=sys.stderr)
    print("📰 朝日新闻 - 今日头条", file=sys.stderr)
    print("="*60, file=sys.stderr)
    
    for news in news_list[:5]:  # 只显示前5条
        print(f"\n[{news['id']}] {news['title']}", file=sys.stderr)
        print(f"    🔗 {news['link']}", file=sys.stderr)
        print(f"    🕒 {news['pubDate']}", file=sys.stderr)
    
    if len(news_list) > 5:
        print(f"\n... 还有 {len(news_list) - 5} 条新闻", file=sys.stderr)
    
    print("\n" + "="*60, file=sys.stderr)


def main():
    """主函数"""
    print("="*60, file=sys.stderr)
    print("📰 朝日新闻RSS抓取工具", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("", file=sys.stderr)
    
    # 获取RSS feed
    feed = fetch_rss_feed(RSS_URL)
    if not feed or not feed.entries:
        print("❌ 未能获取到新闻数据", file=sys.stderr)
        sys.exit(1)
    
    # 转换为JSON格式
    news_list = convert_to_json_format(feed)
    
    # 保存到文件
    filepath = save_to_json(news_list, OUTPUT_DIR)
    if not filepath:
        sys.exit(1)
    
    # 打印摘要
    print_summary(news_list)
    
    # 输出JSON到stdout（可选）
    print(json.dumps(news_list, ensure_ascii=False, indent=2))
    
    print("\n✅ 抓取完成！", file=sys.stderr)


if __name__ == '__main__':
    main()

