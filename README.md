# Skynet - 数据采集与分析系统

一个集成了股票指数、房地产信息等多种数据源的自动化采集和分析系统。

## 📁 项目结构

```
skynet/
├── scripts/              # 数据采集脚本
│   ├── nasdaq_pe.py      # 纳斯达克100 PE比率采集
│   ├── stock_indices.py  # 股票指数数据采集
│   ├── suumo_scraper.py  # Suumo房地产信息爬虫
│   ├── export_to_csv.py  # 数据导出为CSV
│   ├── upload_to_gsheets.py  # 上传到Google Sheets
│   └── mysql_login.sh    # MySQL登录脚本
├── Documents/            # 配置文档
│   ├── db_config.md      # 数据库配置
│   ├── mail_config.md    # 邮件配置
│   ├── rss.md           # RSS配置
│   └── usage.md         # 使用说明
├── output/              # 输出结果文件夹
├── data/                # 临时数据文件夹
└── venv/                # Python虚拟环境
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd skynet

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install selenium webdriver-manager yfinance pymysql gspread google-auth
```

### 2. 数据库配置

使用Docker快速部署MySQL：

```bash
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=finances \
  -p 3306:3306 \
  mysql:8.0
```

详细配置请参考：[Documents/db_config.md](Documents/db_config.md)

## 📊 功能模块

### 1. 股票指数数据采集

**纳斯达克100 PE比率采集**
```bash
python3 scripts/nasdaq_pe.py
```
- 数据源: GuruFocus
- 输出: JSON格式 + MySQL数据库
- 自动保存到 `finances.stock_indices` 表

**股票指数收盘价采集**
```bash
python3 scripts/stock_indices.py
```
- 采集指数: Nasdaq, Nasdaq 100, N225, VIX
- 数据源: Yahoo Finance
- 输出: JSON格式 + MySQL数据库

### 2. 房地产信息采集

**Suumo房源爬虫**
```bash
python3 scripts/suumo_scraper.py
```
- 采集区域: 锦糸町附近（墨田区）
- 类型: 二手公寓（买房）
- 输出: JSON格式

**导出为CSV**
```bash
python3 scripts/export_to_csv.py
```
- 将JSON数据转换为CSV格式
- 可直接导入Google Sheets

### 3. 数据库管理

**登录MySQL**
```bash
./scripts/mysql_login.sh
```

## 📖 详细文档

- [环境配置](Documents/SETUP.md) - 环境搭建详细步骤
- [脚本使用说明](Documents/SCRIPTS.md) - 各脚本功能和参数
- [数据库配置](Documents/db_config.md) - 数据库表结构
- [中文说明](README_ZH.md) - n8n和MySQL部署说明

## 🔧 技术栈

- **Python 3.9+**: 核心开发语言
- **Selenium**: Web爬虫框架
- **yfinance**: 股票数据API
- **PyMySQL**: MySQL数据库连接
- **Google Sheets API**: 数据导出

## 📝 开发者

- 作者: lxy20210816-netizen
- 邮箱: liyuanhua0512@outlook.com

## 📄 许可证

本项目仅供学习和个人使用。

