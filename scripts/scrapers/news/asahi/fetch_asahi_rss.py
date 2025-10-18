#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
朝日新闻RSS抓取脚本
获取朝日新闻RSS feed并保存为JSON格式
支持多个分类的RSS源
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


# RSS链接配置 - 所有分类
RSS_SOURCES = {
    "newsheadlines": {
        "url": "https://www.asahi.com/rss/asahi/newsheadlines.rdf",
        "name": "综合头条",
        "emoji": "📰"
    },
    "national": {
        "url": "https://www.asahi.com/rss/asahi/national.rdf",
        "name": "社会新闻",
        "emoji": "🏘️"
    },
    "international": {
        "url": "https://www.asahi.com/rss/asahi/international.rdf",
        "name": "国际新闻",
        "emoji": "🌏"
    },
    "politics": {
        "url": "https://www.asahi.com/rss/asahi/politics.rdf",
        "name": "政治新闻",
        "emoji": "🏛️"
    },
    "business": {
        "url": "https://www.asahi.com/rss/asahi/business.rdf",
        "name": "经济新闻",
        "emoji": "💼"
    },
    "sports": {
        "url": "https://www.asahi.com/rss/asahi/sports.rdf",
        "name": "体育新闻",
        "emoji": "⚽"
    },
    "culture": {
        "url": "https://www.asahi.com/rss/asahi/culture.rdf",
        "name": "文化新闻",
        "emoji": "🎭"
    },
    "science": {
        "url": "https://www.asahi.com/rss/asahi/science.rdf",
        "name": "科学新闻",
        "emoji": "🔬"
    }
}

# 输出目录
OUTPUT_DIR = os.path.expanduser("~/Desktop/workspace/brain/skynet")


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


def convert_to_json_format(feed, category_key="", category_name="", start_id=1):
    """
    将RSS feed转换为指定的JSON格式
    
    Args:
        feed: feedparser解析后的feed对象
        category_key: 分类键名（如 "national"）
        category_name: 分类名称（如 "社会新闻"）
        start_id: 起始ID
    
    Returns:
        list: JSON格式的新闻列表
    """
    news_list = []
    
    for idx, entry in enumerate(feed.entries, start=start_id):
        news_item = {
            "id": idx,
            "category": category_key,
            "category_name": category_name,
            "title": entry.get('title', ''),
            "link": entry.get('link', ''),
            "pubDate": parse_date(entry),
            "content": entry.get('description', ''),
            "contentSnippet": entry.get('summary', '')
        }
        news_list.append(news_item)
    
    return news_list


def save_to_json(news_list, output_dir, category_stats=None):
    """
    保存新闻列表为JSON文件
    
    Args:
        news_list: 新闻列表
        output_dir: 输出目录
        category_stats: 分类统计信息
    
    Returns:
        str: 保存的文件路径
    """
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名（当前日期）
        today = datetime.now()
        filename = f"asahi_all_news_{today.strftime('%Y%m%d')}.json"
        filepath = os.path.join(output_dir, filename)
        
        # 保存JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存到: {filepath}", file=sys.stderr)
        print(f"📊 共保存 {len(news_list)} 条新闻", file=sys.stderr)
        
        # 显示分类统计
        if category_stats:
            print("\n📋 分类统计:", file=sys.stderr)
            for cat_key, info in category_stats.items():
                print(f"   {info['emoji']} {info['name']}: {info['count']} 条", file=sys.stderr)
        
        return filepath
        
    except Exception as e:
        print(f"❌ 保存文件失败: {e}", file=sys.stderr)
        return None


def print_summary(news_list, category_stats):
    """打印新闻摘要"""
    print("\n" + "="*60, file=sys.stderr)
    print("📰 朝日新闻 - 全分类新闻汇总", file=sys.stderr)
    print("="*60, file=sys.stderr)
    
    # 按分类显示新闻
    for cat_key, info in category_stats.items():
        if info['count'] == 0:
            continue
            
        print(f"\n{info['emoji']} {info['name']} ({info['count']} 条)", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        
        # 获取该分类的前3条新闻
        cat_news = [n for n in news_list if n['category'] == cat_key][:3]
        for news in cat_news:
            print(f"  • {news['title']}", file=sys.stderr)
            print(f"    {news['pubDate']}", file=sys.stderr)
    
    print("\n" + "="*60, file=sys.stderr)


def main():
    """主函数"""
    print("="*60, file=sys.stderr)
    print("📰 朝日新闻RSS抓取工具 - 全分类版", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("", file=sys.stderr)
    
    all_news = []
    category_stats = {}
    
    # 循环抓取所有RSS源
    for cat_key, cat_info in RSS_SOURCES.items():
        print(f"\n{cat_info['emoji']} 正在抓取: {cat_info['name']}", file=sys.stderr)
        
        # 获取RSS feed
        feed = fetch_rss_feed(cat_info['url'])
        
        if not feed or not feed.entries:
            print(f"⚠️  {cat_info['name']} 未能获取数据，跳过", file=sys.stderr)
            category_stats[cat_key] = {
                'name': cat_info['name'],
                'emoji': cat_info['emoji'],
                'count': 0
            }
            continue
        
        # 转换为JSON格式（临时ID，稍后统一编号）
        news_list = convert_to_json_format(
            feed, 
            category_key=cat_key,
            category_name=cat_info['name'],
            start_id=0
        )
        
        # 添加到总列表
        all_news.extend(news_list)
        
        # 统计信息
        category_stats[cat_key] = {
            'name': cat_info['name'],
            'emoji': cat_info['emoji'],
            'count': len(news_list)
        }
    
    if not all_news:
        print("\n❌ 未能获取到任何新闻数据", file=sys.stderr)
        sys.exit(1)
    
    # 统一重新编号
    for idx, news in enumerate(all_news, start=1):
        news['id'] = idx
    
    print(f"\n📊 总计获取 {len(all_news)} 条新闻", file=sys.stderr)
    
    # 保存到文件
    filepath = save_to_json(all_news, OUTPUT_DIR, category_stats)
    if not filepath:
        sys.exit(1)
    
    # 打印摘要
    print_summary(all_news, category_stats)
    
    # 输出JSON到stdout（可选）
    print(json.dumps(all_news, ensure_ascii=False, indent=2))
    
    print("\n✅ 抓取完成！", file=sys.stderr)


if __name__ == '__main__':
    main()

