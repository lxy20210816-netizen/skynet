# Skynet Scripts 工具脚本集合

自动化工具脚本的集合，用于数据抓取、导出和处理。

## 📁 目录结构

```
scripts/
├── scrapers/           🕷️ 爬虫类脚本
│   ├── news/          📰 新闻爬虫
│   │   └── asahi/     朝日新闻RSS抓取
│   ├── social/        💬 社交媒体爬虫
│   │   ├── twitter/   Twitter数据抓取
│   │   └── xueqiu/    雪球数据抓取
│   └── real_estate/   🏠 不动产爬虫
│       └── suumo/     SUUMO房产数据
├── exporters/         📤 数据导出脚本
│   ├── holdings/      持仓数据导出
│   ├── real_estate/   不动产数据导出
│   └── gsheets/       Google Sheets操作
├── finance/           💰 金融数据脚本
│   └── indices/       指数数据获取
└── utils/             🛠️ 工具脚本
    └── database/      数据库工具
```

## 🚀 快速开始

### 环境准备

```bash
# 激活虚拟环境
cd ~/Desktop/workspace/skynet
source venv/bin/activate

# 安装依赖（根据需要）
pip install -r requirements.txt
```

## 📚 各模块说明

### 🕷️ Scrapers - 爬虫类

#### 📰 新闻爬虫

**朝日新闻 (Asahi News)**
- 位置: `scrapers/news/asahi/`
- 功能: 抓取朝日新闻RSS feed
- 文档: [README_ASAHI_RSS.md](scrapers/news/asahi/README_ASAHI_RSS.md)
- 快速运行:
  ```bash
  ./scrapers/news/asahi/sync_asahi_news.sh
  ```

#### 💬 社交媒体爬虫

**Twitter**
- 位置: `scrapers/social/twitter/`
- 功能: Twitter数据抓取和Cookie管理
- 主要脚本:
  - `twitter_selenium.py` - Twitter爬虫主脚本
  - `twitter_save_cookies.py` - 保存登录Cookie
  - `twitter_check.py` - 检查登录状态

**雪球 (Xueqiu)**
- 位置: `scrapers/social/xueqiu/`
- 功能: 抓取雪球用户发文和数据
- 文档: [README_XUEQIU.md](scrapers/social/xueqiu/README_XUEQIU.md)
- 快速运行:
  ```bash
  ./scrapers/social/xueqiu/sync_xueqiu.sh
  ```
- 主要脚本:
  - `xueqiu_scraper.py` - 雪球爬虫（最新版）
  - `xueqiu_with_login.py` - 带登录的雪球爬虫
  - `find_xueqiu_user.py` - 查找雪球用户

#### 🏠 不动产爬虫

**SUUMO**
- 位置: `scrapers/real_estate/suumo/`
- 功能: SUUMO房产数据抓取
- 文档: [SUUMO_USAGE.md](scrapers/real_estate/suumo/SUUMO_USAGE.md)
- 主要脚本:
  - `suumo_scraper.py` - SUUMO爬虫主脚本

### 📤 Exporters - 数据导出

#### 持仓数据导出
- 位置: `exporters/holdings/`
- 功能: 导出持仓数据
- 快速运行:
  ```bash
  ./exporters/holdings/sync_holdings.sh
  ```

#### 不动产数据导出
- 位置: `exporters/real_estate/`
- 功能: 导出不动产数据
- 快速运行:
  ```bash
  ./exporters/real_estate/sync_real_estate.sh
  ```

#### Google Sheets操作
- 位置: `exporters/gsheets/`
- 功能: Google Sheets数据读写和CSV导出
- 文档: [README_export.md](exporters/gsheets/README_export.md)
- 主要脚本:
  - `read_gsheets.py` - 读取Google Sheets
  - `upload_to_gsheets.py` - 上传数据到Google Sheets
  - `export_to_csv.py` - 导出为CSV

### 💰 Finance - 金融数据

#### 指数数据
- 位置: `finance/indices/`
- 功能: 获取股票指数数据
- 主要脚本:
  - `nasdaq_pe.py` - 纳斯达克PE数据
  - `stock_indices.py` - 股票指数数据

### 🛠️ Utils - 工具脚本

#### 数据库工具
- 位置: `utils/database/`
- 功能: 数据库连接和操作
- 主要脚本:
  - `mysql_login.sh` - MySQL登录脚本

## 🔧 配置文件

配置文件统一放在项目根目录的 `config/` 目录：

```
config/
├── twitter_login.json      # Twitter登录信息
├── twitter_cookies.json    # Twitter Cookies
├── xueqiu_login.json       # 雪球登录信息
└── xueqiu_cookies.json     # 雪球Cookies
```

## 📂 输出文件

输出文件统一保存在 `~/Desktop/workspace/brain/skynet/`

## 📝 使用示例

### 抓取朝日新闻
```bash
cd ~/Desktop/workspace/skynet
./scripts/scrapers/news/asahi/sync_asahi_news.sh
```

### 抓取雪球用户发文
```bash
cd ~/Desktop/workspace/skynet
./scripts/scrapers/social/xueqiu/sync_xueqiu.sh
```

### 导出持仓数据
```bash
cd ~/Desktop/workspace/skynet
./scripts/exporters/holdings/sync_holdings.sh
```

### 导出不动产数据
```bash
cd ~/Desktop/workspace/skynet
./scripts/exporters/real_estate/sync_real_estate.sh
```

## 🔄 定时任务

可以使用cron设置定时任务：

```bash
# 编辑crontab
crontab -e

# 每天早上8点抓取朝日新闻
0 8 * * * ~/Desktop/workspace/skynet/scripts/scrapers/news/asahi/sync_asahi_news.sh

# 每天早上9点同步雪球数据
0 9 * * * ~/Desktop/workspace/skynet/scripts/scrapers/social/xueqiu/sync_xueqiu.sh

# 每天晚上10点导出持仓数据
0 22 * * * ~/Desktop/workspace/skynet/scripts/exporters/holdings/sync_holdings.sh
```

## 📖 详细文档

每个模块都有独立的README文档，请查看相应目录：

- 朝日新闻: [scrapers/news/asahi/README_ASAHI_RSS.md](scrapers/news/asahi/README_ASAHI_RSS.md)
- 雪球: [scrapers/social/xueqiu/README_XUEQIU.md](scrapers/social/xueqiu/README_XUEQIU.md)
- SUUMO: [scrapers/real_estate/suumo/SUUMO_USAGE.md](scrapers/real_estate/suumo/SUUMO_USAGE.md)
- Google Sheets: [exporters/gsheets/README_export.md](exporters/gsheets/README_export.md)

## ⚠️ 注意事项

1. **登录信息安全**: 不要将登录配置文件提交到Git
2. **频率控制**: 爬虫请注意访问频率，避免被封禁
3. **数据备份**: 重要数据请定期备份
4. **依赖更新**: 定期更新Python包以获取安全补丁

## 🐛 故障排除

### 常见问题

1. **虚拟环境问题**
   ```bash
   source venv/bin/activate
   ```

2. **依赖缺失**
   ```bash
   pip install feedparser requests selenium
   ```

3. **权限问题**
   ```bash
   chmod +x scripts/scrapers/news/asahi/sync_asahi_news.sh
   ```

## 📞 联系方式

如有问题请查看各模块的详细文档或检查错误日志。

---

**最后更新**: 2025-10-18
