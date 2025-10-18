# 朝日新闻 RSS 抓取工具

## 📰 功能介绍

自动抓取朝日新闻所有分类的 RSS 新闻源，并合并到一个 JSON 文件中。

## 🎯 支持的RSS源

| 分类 | RSS URL | 说明 |
|------|---------|------|
| 📰 综合头条 | `https://www.asahi.com/rss/asahi/newsheadlines.rdf` | 全类别最新头条 |
| 🏘️ 社会新闻 | `https://www.asahi.com/rss/asahi/national.rdf` | 日本国内社会事件 |
| 🌏 国际新闻 | `https://www.asahi.com/rss/asahi/international.rdf` | 国际时事 |
| 🏛️ 政治新闻 | `https://www.asahi.com/rss/asahi/politics.rdf` | 政治动态 |
| 💼 经济新闻 | `https://www.asahi.com/rss/asahi/business.rdf` | 商业经济 |
| ⚽ 体育新闻 | `https://www.asahi.com/rss/asahi/sports.rdf` | 体育赛事 |
| 🎭 文化新闻 | `https://www.asahi.com/rss/asahi/culture.rdf` | 文化艺能 |
| 🔬 科学新闻 | `https://www.asahi.com/rss/asahi/science.rdf` | 科技科学 |

## 📦 安装依赖

```bash
pip install feedparser requests
```

## 🚀 使用方法

### 方法1：直接运行脚本

```bash
cd /Users/eren/Desktop/workspace/skynet
source venv/bin/activate
python3 scripts/scrapers/news/asahi/fetch_asahi_rss.py
```

### 方法2：使用同步脚本（推荐）

```bash
cd /Users/eren/Desktop/workspace/skynet/scripts/scrapers/news/asahi
./sync_asahi_news.sh
```

## 📄 输出格式

### 文件位置
```
~/Desktop/workspace/brain/skynet/asahi_all_news_YYYYMMDD.json
```

### JSON 结构

```json
[
  {
    "id": 1,
    "category": "national",
    "category_name": "社会新闻",
    "title": "新闻标题",
    "link": "https://www.asahi.com/articles/...",
    "pubDate": "2025-10-18 16:30:00",
    "content": "新闻内容",
    "contentSnippet": "内容摘要"
  },
  ...
]
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 新闻编号（全局唯一） |
| `category` | string | 分类键名（如 "national"） |
| `category_name` | string | 分类名称（如 "社会新闻"） |
| `title` | string | 新闻标题 |
| `link` | string | 新闻链接 |
| `pubDate` | string | 发布时间 (YYYY-MM-DD HH:MM:SS) |
| `content` | string | 新闻内容/描述 |
| `contentSnippet` | string | 内容摘要 |

## 📊 数据统计

脚本运行时会显示：
- 每个分类抓取的新闻数量
- 总新闻数量
- 各分类的前3条新闻预览

## ⏰ 定时运行

建议使用 cron 定时任务每小时运行一次：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每小时运行）
0 * * * * /Users/eren/Desktop/workspace/skynet/scripts/scrapers/news/asahi/sync_asahi_news.sh >> /tmp/asahi_rss_cron.log 2>&1
```

## 📝 注意事项

1. **RSS 更新频率**：朝日新闻 RSS 每小时更新一次
2. **新闻数量**：
   - 综合头条：约 40 条
   - 社会新闻：约 40 条  
   - 文化新闻：约 19 条
   - 科学新闻：约 5 条（更新较慢）
3. **时间跨度**：RSS 通常包含最近 1-2 天的新闻
4. **去重建议**：定期运行时建议实现去重机制（根据 link 字段）

## 🔧 自定义配置

### 修改输出目录

编辑 `fetch_asahi_rss.py` 第 72 行：

```python
OUTPUT_DIR = os.path.expanduser("~/your/custom/path")
```

### 选择特定分类

如果只想抓取特定分类，可以在 `fetch_asahi_rss.py` 中注释掉不需要的 RSS 源：

```python
RSS_SOURCES = {
    "newsheadlines": {...},  # 保留
    # "national": {...},     # 注释掉不需要的
    # "international": {...},
    ...
}
```

## 🐛 故障排除

### 问题1：无法获取RSS数据

```bash
# 检查网络连接
curl -I https://www.asahi.com/rss/asahi/newsheadlines.rdf

# 检查依赖
python3 -c "import feedparser, requests; print('OK')"
```

### 问题2：编码错误

确保使用 UTF-8 编码：
```bash
export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8
```

## 📖 相关文档

- [朝日新闻官网](https://www.asahi.com/)
- [RSS 2.0 规范](https://www.rssboard.org/rss-specification)
- [Feedparser 文档](https://feedparser.readthedocs.io/)

## 📧 联系方式

如有问题或建议，请联系项目维护者。
