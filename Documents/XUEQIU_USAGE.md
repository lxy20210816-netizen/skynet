# 雪球爬虫使用指南

## 📌 快速开始

### 1. 获取用户ID

段永平（大道无形我有型）的雪球用户ID是：**`9528875558`**

#### 如何查找其他用户的ID？

1. 访问 https://xueqiu.com
2. 在搜索框搜索用户名（如"大道无形我有型"）
3. 点击用户头像进入主页
4. 查看浏览器地址栏，格式为：`https://xueqiu.com/u/9528875558`
5. 最后一串数字就是用户ID

### 2. 运行爬虫

#### 方法一：使用Shell脚本（推荐）

```bash
cd ~/Desktop/workspace/skynet
./scripts/sync_xueqiu.sh
```

#### 方法二：直接使用Python脚本

```bash
cd ~/Desktop/workspace/skynet
source venv/bin/activate

# 抓取段永平的发文（最多50条）
python3 scripts/xueqiu_scraper.py \
    --user-id 9528875558 \
    --max-posts 50 \
    --output output/xueqiu_duanyongping.json \
    --format both
```

### 3. 参数说明

- `--user-id`: 雪球用户ID（必填）
- `--max-posts`: 最多抓取的发文数量（默认20）
- `--output`: 输出JSON文件路径
- `--format`: 输出格式
  - `json`: 仅JSON格式
  - `markdown`: 仅Markdown格式
  - `both`: 同时输出JSON和Markdown（默认）
- `--visible`: 显示浏览器窗口（调试用）
- `--headless`: 无头模式（默认）

## 📊 输出文件

### JSON文件示例

```json
[
  {
    "id": "123456789",
    "user_id": "9528875558",
    "username": "大道无形我有型",
    "title": "关于投资的一些思考",
    "content": "...",
    "url": "https://xueqiu.com/9528875558/123456789",
    "published_at": "2024-12-01 10:30",
    "likes": "128",
    "comments": "45",
    "retweets": "23",
    "scraped_at": "2025-10-16T01:30:00"
  }
]
```

### Markdown文件示例

```markdown
# 📊 大道无形我有型 - 雪球发文

📅 抓取时间：2025年10月16日 01:30
📝 发文数量：50条

---

## 1. 关于投资的一些思考

🕒 **发布时间**: 2024-12-01 10:30
🔗 **链接**: https://xueqiu.com/9528875558/123456789

投资内容...

*👍 128 赞 | 💬 45 评论 | 🔄 23 转发*

---
```

## ⚠️ 重要提示

1. **段永平已暂停发文**：自2025年4月10日起，段永平宣布暂时不再发雪球，因此抓取的是历史发文。

2. **反爬虫机制**：雪球有反爬虫机制，建议：
   - 不要频繁抓取
   - 适当增加延迟时间
   - 使用`--visible`模式观察是否被检测

3. **登录状态**：某些内容可能需要登录才能查看。如需登录功能，请参考`twitter_selenium.py`的登录实现。

## 🛠️ 故障排除

### 问题1：无法找到元素

**原因**：雪球页面结构可能更新
**解决**：使用`--visible`模式查看页面，手动调整CSS选择器

### 问题2：抓取数量不足

**原因**：需要滚动加载更多内容
**解决**：增加`max_scrolls`参数或延长等待时间

### 问题3：被检测为机器人

**原因**：频繁访问触发反爬虫
**解决**：
- 增加延迟时间
- 使用代理IP
- 手动登录后保存cookies

## 📝 示例用法

### 抓取最近20条发文

```bash
python3 scripts/xueqiu_scraper.py --user-id 9528875558 --max-posts 20
```

### 抓取100条发文并显示浏览器

```bash
python3 scripts/xueqiu_scraper.py \
    --user-id 9528875558 \
    --max-posts 100 \
    --visible
```

### 仅输出Markdown格式

```bash
python3 scripts/xueqiu_scraper.py \
    --user-id 9528875558 \
    --format markdown > output/duanyongping.md
```

## 🔗 相关链接

- 段永平雪球主页: https://xueqiu.com/u/9528875558
- 雪球官网: https://xueqiu.com
- 项目文档: /Documents/PROJECT_OVERVIEW.md





