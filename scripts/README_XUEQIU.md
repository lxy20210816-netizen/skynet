# 雪球爬虫 - 快速使用指南

## 🎯 功能

抓取雪球用户的发文内容，支持：
- 自动滚动加载更多内容
- 提取标题、内容、发布时间
- 统计点赞、评论、转发数
- 输出JSON和Markdown格式

## 🚀 快速开始

### 方式一：一键运行（推荐）

```bash
cd /Users/a0000/Desktop/workspace/skynet
./scripts/sync_xueqiu.sh
```

这将抓取段永平（大道无形我有型）的最近50条发文。

### 方式二：自定义参数

```bash
cd /Users/a0000/Desktop/workspace/skynet
source venv/bin/activate

# 基本用法
python3 scripts/xueqiu_scraper.py --user-id 9528875558

# 抓取更多发文
python3 scripts/xueqiu_scraper.py --user-id 9528875558 --max-posts 100

# 显示浏览器窗口（调试）
python3 scripts/xueqiu_scraper.py --user-id 9528875558 --visible

# 仅输出Markdown
python3 scripts/xueqiu_scraper.py --user-id 9528875558 --format markdown
```

## 📋 命令参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--user-id` | 雪球用户ID | 9528875558（段永平） |
| `--max-posts` | 最多抓取的发文数 | 20 |
| `--output` | 输出文件路径 | ../output/xueqiu_posts.json |
| `--format` | 输出格式（json/markdown/both） | both |
| `--visible` | 显示浏览器窗口 | False |

## 📂 输出文件

抓取完成后，文件保存在 `output/` 目录：

- `xueqiu_duanyongping.json` - JSON格式数据
- `xueqiu_duanyongping.md` - Markdown格式（方便阅读）

## 👤 其他用户

要抓取其他雪球用户：

1. 访问 https://xueqiu.com 搜索用户
2. 进入用户主页，URL格式：`https://xueqiu.com/u/[用户ID]`
3. 复制用户ID
4. 运行：`python3 scripts/xueqiu_scraper.py --user-id [用户ID]`

### 示例：抓取其他知名投资人

```bash
# 方三文（雪球创始人）- 示例ID
python3 scripts/xueqiu_scraper.py --user-id 1955602780

# 其他用户...
python3 scripts/xueqiu_scraper.py --user-id [用户ID] --max-posts 30
```

## ⚠️ 注意事项

1. **段永平已暂停发文**（2025年4月起），抓取的是历史内容
2. 雪球有反爬虫机制，建议适度使用，避免频繁抓取
3. 首次运行会自动安装 `selenium` 依赖
4. 需要安装Chrome浏览器

## 🔧 故障排除

### 问题：找不到Chrome浏览器
```bash
# macOS安装Chrome
brew install --cask google-chrome
```

### 问题：找不到元素/抓取失败
使用可见模式查看页面：
```bash
python3 scripts/xueqiu_scraper.py --user-id 9528875558 --visible
```

### 问题：抓取的内容不完整
增加最大发文数和滚动次数：
```bash
python3 scripts/xueqiu_scraper.py --user-id 9528875558 --max-posts 100
```

## 📚 相关文档

- 详细使用文档：`/Documents/XUEQIU_USAGE.md`
- 项目总览：`/Documents/PROJECT_OVERVIEW.md`
- Twitter爬虫：`scripts/README.md`

## 🔗 相关链接

- 段永平雪球主页：https://xueqiu.com/u/9528875558
- 雪球首页：https://xueqiu.com

