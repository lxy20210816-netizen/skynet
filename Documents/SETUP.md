# 环境配置指南

本文档详细说明Skynet项目的环境搭建步骤。

## 📋 系统要求

- Python 3.9+
- Google Chrome浏览器
- MySQL 8.0+
- Docker（可选，用于快速部署）

## 🔧 安装步骤

### 1. Python虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install selenium webdriver-manager yfinance pymysql gspread google-auth google-auth-oauthlib google-api-python-client
```

### 2. MySQL数据库

#### 方法1: Docker部署（推荐）

```bash
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=finances \
  -p 3306:3306 \
  mysql:8.0
```

#### 方法2: 本地安装

根据您的操作系统安装MySQL 8.0，然后创建数据库：

```sql
CREATE DATABASE finances CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE finances;

-- 创建stock_indices表
CREATE TABLE `stock_indices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `nasdaq` decimal(12,3) NOT NULL,
  `nasdaq_100` decimal(12,3) NOT NULL,
  `nasdaq_100_pe` decimal(12,3) NOT NULL,
  `n225` decimal(12,3) NOT NULL,
  `vix` decimal(12,3) NOT NULL,
  `a` decimal(12,3) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

### 3. Git配置

```bash
# 配置用户信息
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

### 4. Chrome浏览器

确保已安装Google Chrome浏览器。ChromeDriver会由`webdriver-manager`自动下载和管理。

## ✅ 验证安装

### 测试数据库连接

```bash
./scripts/mysql_login.sh
```

### 测试股票数据采集

```bash
source venv/bin/activate
python3 scripts/stock_indices.py
```

如果看到JSON输出且包含`"database_saved": true`，说明环境配置成功！

### 测试爬虫功能

```bash
python3 scripts/suumo_scraper.py
```

## 🔐 Google Sheets API配置（可选）

如果需要直接上传数据到Google Sheets：

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目
3. 启用 **Google Sheets API** 和 **Google Drive API**
4. 创建服务账号并下载JSON密钥
5. 将密钥保存为项目根目录的 `credentials.json`
6. 在Google Sheets中与服务账号邮箱共享您的表格

## 📦 依赖包列表

```
selenium>=4.35.0
webdriver-manager>=4.0.2
yfinance>=0.2.66
pymysql>=1.1.2
gspread>=6.2.1
google-auth>=2.41.1
google-api-python-client>=2.184.0
```

## ⚠️ 常见问题

### Q1: ChromeDriver下载失败
**A:** 检查网络连接，或手动下载ChromeDriver并配置路径。

### Q2: 数据库连接失败
**A:** 确认MySQL服务正在运行，检查用户名密码是否正确。

### Q3: Selenium无法启动浏览器
**A:** 确保已安装Chrome浏览器，尝试更新Chrome到最新版本。

## 📞 技术支持

如有问题，请查看各脚本的详细说明：[Documents/SCRIPTS.md](SCRIPTS.md)

