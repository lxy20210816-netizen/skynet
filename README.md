# Skynet - 数据采集与分析系统

> 一个集成了股票指数、房地产信息等多种数据源的自动化采集和分析系统。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 目录

- [快速开始](#-快速开始)
- [功能模块](#-功能模块)
- [项目结构](#-项目结构)
- [详细文档](#-详细文档)
- [技术栈](#-技术栈)

## 📁 项目结构

```
skynet/
├── 📄 README.md              # 项目主页
├── 📄 QUICKSTART.md          # 5分钟快速入门
├── 📄 STRUCTURE.md           # 项目结构详解
├── 📄 requirements.txt       # Python依赖
│
├── 📁 config/                # 配置文件
│   └── credentials.json      # Google API凭证
│
├── 📁 scripts/               # 核心脚本（8个）
│   ├── nasdaq_pe.py          # 纳斯达克100 PE比率
│   ├── stock_indices.py      # 股票指数数据
│   ├── suumo_scraper.py      # Suumo房源爬虫
│   ├── export_to_csv.py      # 数据导出CSV
│   ├── upload_to_gsheets.py  # 上传Google Sheets
│   ├── read_gsheets.py       # 读取Google Sheets
│   └── mysql_login.sh        # MySQL登录
│
├── 📁 Documents/             # 文档中心（8个）
│   ├── PROJECT_OVERVIEW.md   # 项目概览
│   ├── SETUP.md              # 环境配置
│   ├── SCRIPTS.md            # 脚本手册
│   ├── GOOGLE_SHEETS.md      # Google Sheets集成
│   └── db_config.md          # 数据库配置
│
├── 📁 output/                # 输出结果
├── 📁 data/                  # 临时数据
└── 📁 venv/                  # Python虚拟环境
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

**使用Docker快速部署MySQL：**

```bash
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=finances \
  -p 3306:3306 \
  mysql:8.0

# 确认运行状态
docker ps
```

### 3. n8n自动化（可选）

**方式1：npx运行（推荐 - 无需安装）**

```bash
# 直接运行（首次会自动下载）
npx n8n

# 或者后台运行
nohup npx n8n > n8n.log 2>&1 &
```

**方式2：全局安装**

```bash
# 安装n8n
npm install -g n8n

# 启动n8n
n8n
```

**方式3：Docker部署**

```bash
docker volume create n8n_data
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n

# 后台运行把 -it --rm 改为 -d
```

访问 http://localhost:5678 打开n8n界面。

**重要提示：** 
- npx/npm方式可以直接使用 `localhost` 或 `127.0.0.1` 访问MySQL
- Docker部署需要使用宿主机IP地址（使用 `ifconfig` 查看）
- 参考：https://github.com/n8n-io/n8n

详细配置请参考：[Documents/SETUP.md](Documents/SETUP.md)

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

### 3. Google Sheets集成（可选）

**读取Google Sheets数据：**
```bash
python3 scripts/read_gsheets.py "YOUR_SHEET_ID" -o output/data.json
```

**上传数据到Google Sheets：**
```bash
python3 scripts/export_to_csv.py  # 先转换为CSV
```

详细配置请参考：[Documents/GOOGLE_SHEETS.md](Documents/GOOGLE_SHEETS.md)

### 4. 数据库管理

**登录MySQL**
```bash
./scripts/mysql_login.sh

# 查询数据
SELECT * FROM stock_indices ORDER BY date DESC LIMIT 10;
```

## 📖 详细文档

- [⚡ 快速入门](QUICKSTART.md) - 5分钟上手指南
- [🏗️ 项目结构](STRUCTURE.md) - 目录组织说明
- [📋 项目概览](Documents/PROJECT_OVERVIEW.md) - 系统架构设计
- [⚙️ 环境配置](Documents/SETUP.md) - 详细安装步骤
- [📜 脚本手册](Documents/SCRIPTS.md) - 各脚本使用方法
- [📊 Google Sheets](Documents/GOOGLE_SHEETS.md) - 数据导入导出
- [🗄️ 数据库配置](Documents/db_config.md) - 表结构说明

## 🔧 技术栈

- **Python 3.9+**: 核心开发语言
- **Selenium**: Web爬虫框架
- **yfinance**: 股票数据API
- **PyMySQL**: MySQL数据库连接
- **Google Sheets API**: 数据导出

## 🎯 主要特性

✅ **自动化数据采集** - 股票、房地产等多源数据  
✅ **结构化存储** - MySQL数据库持久化  
✅ **Google Sheets集成** - 读取/写入云端表格  
✅ **数据导出** - 支持JSON、CSV等格式  
✅ **n8n兼容** - 可集成到自动化工作流  
✅ **完整文档** - 从入门到精通的全套指南  

## 🔄 自动化运行

### 定时任务（Crontab）

```bash
# 每天早上9点采集股票数据
0 9 * * * cd /path/to/skynet && source venv/bin/activate && python3 scripts/stock_indices.py

# 每天早上9:30采集PE比率
30 9 * * * cd /path/to/skynet && source venv/bin/activate && python3 scripts/nasdaq_pe.py

# 每周一早上10点同步Google Sheets
0 10 * * 1 cd /path/to/skynet && source venv/bin/activate && python3 scripts/read_gsheets.py "SHEET_ID" -o output/weekly.json
```

## 📝 开发者

- 👤 作者: lxy20210816-netizen
- 📧 邮箱: liyuanhua0512@outlook.com
- 🔗 GitHub: [skynet](https://github.com/your-username/skynet)

## 📄 许可证

本项目仅供学习和个人使用。使用爬虫功能请遵守目标网站的使用条款。

## ⭐ Star History

如果这个项目对您有帮助，欢迎给个Star！

