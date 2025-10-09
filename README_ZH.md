# Skynet - 数据采集与分析系统（中文说明）

## 🚀 快速开始

### 1. 环境安装

```bash
# 克隆项目
git clone <repository-url>
cd skynet

# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 安装MySQL（使用Docker）

```bash
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=finances \
  -p 3306:3306 \
  mysql:8.0
```

确认运行状态：
```bash
docker ps
```

### 3. 安装n8n（可选）

如果需要使用n8n自动化工作流：

```bash
docker volume create n8n_data
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

访问 http://localhost:5678 打开n8n界面。

**重要：** n8n访问MySQL时，不能使用127.0.0.1，应该使用本机IP地址：

```bash
# 查看本机IP
ifconfig
# 找到类似 en0 或 wlan0 的网卡下的IP，例如：
# inet 192.168.1.100
```

## 📊 功能说明

### 股票数据采集

```bash
# 采集股票指数（Nasdaq, N225, VIX等）
python3 scripts/stock_indices.py

# 采集纳斯达克100 PE比率
python3 scripts/nasdaq_pe.py
```

数据自动保存到MySQL数据库。

### 房地产数据采集

```bash
# 抓取Suumo房源信息（锦糸町附近）
python3 scripts/suumo_scraper.py > output/房源数据.json 2>&1

# 转换为CSV格式
python3 scripts/export_to_csv.py

# CSV文件可直接导入Google Sheets
```

### 数据库管理

```bash
# 登录MySQL
./scripts/mysql_login.sh

# 查询最新数据
SELECT * FROM stock_indices ORDER BY date DESC LIMIT 10;
```

## 📁 项目结构

```
skynet/
├── scripts/              # 所有脚本
│   ├── nasdaq_pe.py      # PE比率采集
│   ├── stock_indices.py  # 股票指数采集
│   ├── suumo_scraper.py  # 房源爬虫
│   ├── export_to_csv.py  # 导出CSV
│   └── mysql_login.sh    # 数据库登录
├── Documents/            # 文档
│   ├── SETUP.md          # 环境配置
│   ├── SCRIPTS.md        # 脚本说明
│   └── PROJECT_OVERVIEW.md # 项目概览
├── output/              # 输出文件
├── data/                # 临时数据
└── requirements.txt     # Python依赖
```

## 📖 详细文档

- [项目概览](Documents/PROJECT_OVERVIEW.md) - 了解系统架构
- [环境配置](Documents/SETUP.md) - 详细安装步骤
- [脚本使用](Documents/SCRIPTS.md) - 各脚本的使用方法
- [数据库配置](Documents/db_config.md) - 表结构说明

## 🎯 主要特性

✅ 自动化数据采集  
✅ 结构化数据存储  
✅ 支持导出到Google Sheets  
✅ 兼容n8n工作流  
✅ 完整的错误处理  
✅ 详细的使用文档  

## 👨‍💻 开发者

- 作者: lxy20210816-netizen
- 邮箱: liyuanhua0512@outlook.com

## 📝 许可

仅供个人学习使用。使用爬虫功能请遵守目标网站的使用条款。

