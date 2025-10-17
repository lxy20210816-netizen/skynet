# 朝日新闻RSS抓取工具

## 📌 功能说明

自动获取朝日新闻RSS feed，并保存为JSON格式文件。

## 🚀 快速开始

### 安装依赖

```bash
cd /Users/a0000/Desktop/workspace/skynet
source venv/bin/activate
pip install feedparser requests
```

### 运行脚本

```bash
# 基本用法
python3 scripts/fetch_asahi_rss.py

# 或者直接运行
./scripts/fetch_asahi_rss.py
```

## 📊 输出格式

### 文件命名

文件名格式：`asahi_newsheadlines_YYYYMMDD.json`

例如：
- 2025年10月18日执行 → `asahi_newsheadlines_20251018.json`
- 2025年10月19日执行 → `asahi_newsheadlines_20251019.json`

### JSON数据结构

```json
[
  {
    "id": 1,
    "title": "阪神・森下がサヨナラ2ラン　「自分もびっくりしたけど最高の結果」",
    "link": "http://www.asahi.com/articles/ASTBJ4Q78TBJPTQP00GM.html?ref=rss",
    "pubDate": "2025-10-16 14:20:55",
    "content": "",
    "contentSnippet": ""
  },
  {
    "id": 2,
    "title": "...",
    "link": "...",
    "pubDate": "...",
    "content": "",
    "contentSnippet": ""
  }
]
```

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `id` | 新闻序号 | 1, 2, 3... |
| `title` | 新闻标题 | "阪神・森下がサヨナラ2ラン..." |
| `link` | 新闻链接 | "http://www.asahi.com/articles/..." |
| `pubDate` | 发布时间 | "2025-10-16 14:20:55" |
| `content` | 新闻内容（通常为空） | "" |
| `contentSnippet` | 内容摘要（通常为空） | "" |

## 📂 文件位置

### 脚本位置
```
/Users/a0000/Desktop/workspace/skynet/scripts/fetch_asahi_rss.py
```

### 输出位置
```
/Users/a0000/Desktop/workspace/brain/skynet/asahi_newsheadlines_YYYYMMDD.json
```

## 🔧 脚本配置

在脚本中可以修改以下配置：

```python
# RSS链接
RSS_URL = "https://www.asahi.com/rss/asahi/newsheadlines.rdf"

# 输出目录
OUTPUT_DIR = "/Users/a0000/Desktop/workspace/brain/skynet"
```

## 📝 运行示例

```bash
$ python3 scripts/fetch_asahi_rss.py

============================================================
📰 朝日新闻RSS抓取工具
============================================================

📡 正在获取RSS: https://www.asahi.com/rss/asahi/newsheadlines.rdf
✅ 成功获取 40 条新闻
💾 数据已保存到: /Users/a0000/Desktop/workspace/brain/skynet/asahi_newsheadlines_20251018.json
📊 共保存 40 条新闻

============================================================
📰 朝日新闻 - 今日头条
============================================================

[1] 岩手県警、知識不足で外国人を誤認逮捕　すでに釈放、公表2日遅れ
    🔗 http://www.asahi.com/articles/ASTBK4VY2TBKUJUB00XM.html?ref=rss
    🕒 2025-10-17 15:13:05

[2] 市の参事を収賄容疑で逮捕　修繕工事めぐり電動自転車受け取ったか
    🔗 http://www.asahi.com/articles/ASTBK4VDCTBKPTIL01GM.html?ref=rss
    🕒 2025-10-17 14:49:38

... 还有 35 条新闻

============================================================

✅ 抓取完成！
```

## 🔄 定时任务

可以使用cron定时执行脚本：

```bash
# 编辑crontab
crontab -e

# 每天早上8点执行
0 8 * * * cd /Users/a0000/Desktop/workspace/skynet && source venv/bin/activate && python3 scripts/fetch_asahi_rss.py >> /tmp/asahi_rss.log 2>&1
```

## 📋 新闻分类

朝日新闻RSS包含以下分类的新闻：

- 📰 社会新闻
- ⚽ 体育新闻
- 💼 商业新闻
- 🏛️ 政治新闻
- 🌍 国际新闻
- 🎭 文化娱乐
- 🔬 科学技术
- 🕊️ 讣告

## 📈 数据处理示例

### Python读取JSON

```python
import json

# 读取JSON文件
with open('/Users/a0000/Desktop/workspace/brain/skynet/asahi_newsheadlines_20251018.json', 'r', encoding='utf-8') as f:
    news_list = json.load(f)

# 打印前5条新闻标题
for news in news_list[:5]:
    print(f"{news['id']}. {news['title']}")
    print(f"   {news['link']}")
    print(f"   {news['pubDate']}")
    print()
```

### 筛选特定类型新闻

```python
# 筛选体育新闻（包含关键词）
sports_news = [
    news for news in news_list 
    if any(keyword in news['title'] for keyword in ['阪神', '大谷', '佐々木', 'ドジャース'])
]

# 按时间排序
sorted_news = sorted(news_list, key=lambda x: x['pubDate'], reverse=True)
```

## ⚠️ 注意事项

1. **网络连接**：需要稳定的网络连接访问朝日新闻
2. **编码问题**：所有文件使用UTF-8编码
3. **数据更新**：RSS feed实时更新，每次抓取结果可能不同
4. **内容字段**：朝日新闻RSS的`content`和`contentSnippet`通常为空，只提供标题和链接

## 🔗 相关链接

- 朝日新闻官网：https://www.asahi.com/
- RSS Feed源：https://www.asahi.com/rss/asahi/newsheadlines.rdf

## 📞 问题反馈

如有问题请查看脚本中的错误提示信息。

