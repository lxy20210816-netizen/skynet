#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雪球API爬虫（推荐）
使用雪球公开API获取用户发文，比Selenium更稳定快速
"""

import sys
import json
import time
import argparse
import os
from datetime import datetime

try:
    import requests
except ImportError:
    print("❌ 请先安装requests: pip install requests", file=sys.stderr)
    sys.exit(1)


# 段永平的雪球ID
DEFAULT_USER_ID = "9528875558"


class XueqiuAPI:
    """雪球API客户端"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://xueqiu.com',
        })
        self.base_url = "https://xueqiu.com"
    
    def init_cookies(self):
        """初始化cookies - 访问首页获取必要的cookies"""
        try:
            print("🔐 初始化cookies...", file=sys.stderr)
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print("✅ Cookies初始化成功", file=sys.stderr)
                return True
            else:
                print(f"⚠️  初始化cookies失败: {response.status_code}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"❌ 初始化失败: {e}", file=sys.stderr)
            return False
    
    def get_user_info(self, user_id):
        """获取用户信息"""
        try:
            url = f"https://stock.xueqiu.com/v5/stock/portfolio/stock/list.json"
            params = {
                'user_id': user_id,
                'size': 1
            }
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"⚠️  获取用户信息失败: {response.status_code}", file=sys.stderr)
                return None
        
        except Exception as e:
            print(f"❌ 获取用户信息失败: {e}", file=sys.stderr)
            return None
    
    def get_user_posts(self, user_id, max_posts=20):
        """
        获取用户发文列表
        
        Args:
            user_id: 雪球用户ID
            max_posts: 最多获取的发文数
        
        Returns:
            list: 发文列表
        """
        posts = []
        page = 1
        page_size = 20  # 每页20条
        
        try:
            # 访问用户主页获取用户名
            print(f"📖 正在访问用户主页...", file=sys.stderr)
            user_page_url = f"{self.base_url}/u/{user_id}"
            user_response = self.session.get(user_page_url)
            
            # 尝试从页面提取用户名（可选）
            username = f"User_{user_id}"
            
            print(f"👤 用户ID: {user_id}", file=sys.stderr)
            print(f"📝 开始获取发文...", file=sys.stderr)
            
            while len(posts) < max_posts:
                # 雪球用户动态API
                api_url = f"https://xueqiu.com/statuses/original/timeline.json"
                params = {
                    'user_id': user_id,
                    'page': page,
                    'type': 0,  # 0=全部, 2=原创
                }
                
                print(f"📄 正在获取第 {page} 页...", file=sys.stderr)
                response = self.session.get(api_url, params=params)
                
                if response.status_code != 200:
                    print(f"⚠️  API请求失败: {response.status_code}", file=sys.stderr)
                    # 打印响应内容供调试
                    print(f"响应: {response.text[:200]}", file=sys.stderr)
                    break
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    print(f"❌ JSON解析失败", file=sys.stderr)
                    break
                
                # 检查返回的数据结构
                if 'list' not in data:
                    print(f"⚠️  返回数据格式异常: {list(data.keys())}", file=sys.stderr)
                    break
                
                page_posts = data.get('list', [])
                
                if not page_posts:
                    print(f"📭 没有更多发文了", file=sys.stderr)
                    break
                
                for post in page_posts:
                    if len(posts) >= max_posts:
                        break
                    
                    # 提取发文数据
                    post_data = self._extract_post_data(post, user_id)
                    posts.append(post_data)
                    
                    title = post_data.get('title', '')[:50]
                    print(f"✅ [{len(posts)}/{max_posts}] {title}...", file=sys.stderr)
                
                page += 1
                time.sleep(1)  # 避免请求过快
            
            print(f"\n✅ 共获取 {len(posts)} 条发文", file=sys.stderr)
            return posts
        
        except Exception as e:
            print(f"❌ 获取发文失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return posts
    
    def _extract_post_data(self, post, user_id):
        """提取发文数据"""
        post_data = {
            'id': str(post.get('id', '')),
            'user_id': user_id,
            'username': post.get('user', {}).get('screen_name', ''),
            'user_description': post.get('user', {}).get('description', ''),
            'title': post.get('title', ''),
            'text': post.get('text', ''),
            'description': post.get('description', ''),
            'created_at': post.get('created_at'),
            'source': post.get('source', ''),
            'like_count': post.get('like_count', 0),
            'reply_count': post.get('reply_count', 0),
            'retweet_count': post.get('retweet_count', 0),
            'fav_count': post.get('fav_count', 0),
            'view_count': post.get('view_count', 0),
            'url': f"https://xueqiu.com/{user_id}/{post.get('id', '')}",
            'scraped_at': datetime.now().isoformat()
        }
        
        # 格式化时间
        if post_data['created_at']:
            try:
                timestamp = post_data['created_at'] / 1000  # 毫秒转秒
                dt = datetime.fromtimestamp(timestamp)
                post_data['published_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                post_data['published_at'] = ''
        
        return post_data


def save_to_file(posts, output_file):
    """保存数据到文件"""
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 JSON已保存到: {output_file}", file=sys.stderr)
        return True
    
    except Exception as e:
        print(f"❌ 保存文件失败: {e}", file=sys.stderr)
        return False


def format_to_markdown(posts, user_id=""):
    """将发文格式化为Markdown"""
    username = posts[0].get('username', f'User_{user_id}') if posts else ''
    
    lines = [
        f"# 📊 {username} 的雪球发文\n",
        f"📅 抓取时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n",
        f"📝 发文数量：{len(posts)}条\n",
        f"🔗 用户主页：https://xueqiu.com/u/{user_id}\n",
        "---\n",
    ]
    
    for i, post in enumerate(posts, 1):
        # 标题
        title = post.get('title') or post.get('text', '')[:50] or '无标题'
        lines.append(f"\n## {i}. {title}\n")
        
        # 发布时间和来源
        pub_time = post.get('published_at', '')
        source = post.get('source', '')
        if pub_time:
            time_str = f"🕒 **发布时间**: {pub_time}"
            if source:
                time_str += f" | 来自: {source}"
            lines.append(f"{time_str}\n")
        
        # 链接
        if post.get('url'):
            lines.append(f"🔗 **链接**: {post['url']}\n")
        
        # 正文内容
        text = post.get('text') or post.get('description', '')
        if text:
            # 清理HTML标签（简单处理）
            import re
            clean_text = re.sub(r'<[^>]+>', '', text)
            clean_text = clean_text.replace('&nbsp;', ' ').replace('&quot;', '"')
            lines.append(f"\n{clean_text}\n")
        
        # 互动数据
        stats = []
        if post.get('like_count'):
            stats.append(f"👍 {post['like_count']} 赞")
        if post.get('reply_count'):
            stats.append(f"💬 {post['reply_count']} 评论")
        if post.get('retweet_count'):
            stats.append(f"🔄 {post['retweet_count']} 转发")
        if post.get('view_count'):
            stats.append(f"👁️ {post['view_count']} 阅读")
        
        if stats:
            lines.append(f"\n*{' | '.join(stats)}*\n")
        
        lines.append("\n---\n")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='雪球API爬虫（推荐使用）')
    parser.add_argument('--user-id', type=str, default=DEFAULT_USER_ID,
                        help=f'雪球用户ID (默认: {DEFAULT_USER_ID} - 段永平)')
    parser.add_argument('--max-posts', type=int, default=20,
                        help='最多获取的发文数量 (默认: 20)')
    parser.add_argument('--output', type=str, default='../output/xueqiu_posts.json',
                        help='输出文件路径')
    parser.add_argument('--format', type=str, choices=['json', 'markdown', 'both'], default='both',
                        help='输出格式 (默认: both)')
    
    args = parser.parse_args()
    
    print("=" * 60, file=sys.stderr)
    print("📊 雪球API爬虫", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"👤 用户ID: {args.user_id}", file=sys.stderr)
    print(f"📝 最多获取: {args.max_posts}条", file=sys.stderr)
    print(f"💾 输出格式: {args.format}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("", file=sys.stderr)
    
    # 创建API客户端
    api = XueqiuAPI()
    
    # 初始化cookies
    if not api.init_cookies():
        print("⚠️  Cookies初始化失败，继续尝试...", file=sys.stderr)
    
    time.sleep(1)
    
    # 获取发文
    posts = api.get_user_posts(args.user_id, args.max_posts)
    
    if not posts:
        print("❌ 没有获取到任何发文", file=sys.stderr)
        print("\n💡 可能的原因：", file=sys.stderr)
        print("   1. 用户ID不正确", file=sys.stderr)
        print("   2. 用户没有公开发文", file=sys.stderr)
        print("   3. API访问受限（需要登录）", file=sys.stderr)
        print(f"\n请访问 https://xueqiu.com/u/{args.user_id} 确认用户ID", file=sys.stderr)
        return
    
    # 保存数据
    if args.format in ['json', 'both']:
        save_to_file(posts, args.output)
    
    if args.format in ['markdown', 'both']:
        markdown_file = args.output.replace('.json', '.md')
        markdown_content = format_to_markdown(posts, args.user_id)
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"📝 Markdown已保存到: {markdown_file}", file=sys.stderr)
    
    # 输出到stdout
    if args.format == 'markdown':
        print(format_to_markdown(posts, args.user_id))
    else:
        print(json.dumps(posts, ensure_ascii=False, indent=2))
    
    print("\n✅ 抓取完成！", file=sys.stderr)


if __name__ == '__main__':
    main()

