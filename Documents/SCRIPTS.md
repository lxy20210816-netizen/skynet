# 脚本使用说明

本文档详细介绍各个脚本的功能、参数和使用方法。

## 📈 股票数据采集脚本

### nasdaq_pe.py - 纳斯达克100 PE比率采集

**功能：** 从GuruFocus网站采集纳斯达克100指数的PE比率数据。

**数据源：** https://www.gurufocus.com/

**使用方法：**
```bash
source venv/bin/activate
python3 scripts/nasdaq_pe.py
```

**输出格式：**
```json
{
  "success": true,
  "data": {
    "pe_ratio": 33.38,
    "date": "2025-10-01",
    "source": "GuruFocus",
    "timestamp": "2025-10-03T00:13:28.635885",
    "description": "Nasdaq 100 PE Ratio: 33.38 (As of 2025-10-01)"
  },
  "database_saved": true
}
```

**数据库：** 自动保存到 `finances.stock_indices` 表的 `nasdaq_100_pe` 字段

**特点：**
- 使用Selenium模拟真实浏览器
- 绕过反爬虫机制
- 自动重试和错误处理
- 支持无头模式运行

---

### stock_indices.py - 股票指数数据采集

**功能：** 使用Yahoo Finance API采集主要股票指数的收盘价。

**采集指数：**
- Nasdaq综合指数 (^IXIC)
- Nasdaq 100指数 (^NDX)
- 日经225指数 (^N225)
- VIX恐慌指数 (^VIX)

**使用方法：**
```bash
python3 scripts/stock_indices.py
```

**输出格式：**
```json
{
  "success": true,
  "data": {
    "date": "2025-10-02",
    "nasdaq": 22776.828125,
    "nasdaq_100": 24821.869140625,
    "n225": 44936.73046875,
    "vix": 16.770000457763672,
    "timestamp": "2025-10-03T00:46:46.635577"
  },
  "database_saved": true
}
```

**数据库：** 自动保存到 `finances.stock_indices` 表

**注意事项：**
- 获取的是前一个交易日的收盘价
- 数据库中的date字段为该交易日的日期
- 如果该日期已存在，会更新数据而不是插入新记录

---

## 🏠 房地产数据采集脚本

### suumo_scraper.py - Suumo房源爬虫

**功能：** 抓取Suumo网站的房地产信息（当前配置为买房信息）。

**当前配置：**
- 区域: 墨田区（锦糸町附近）
- 类型: 二手公寓（中古マンション）
- 页数: 最多3页（约90个房源）

**使用方法：**
```bash
python3 scripts/suumo_scraper.py > output/suumo_data.json 2>&1
```

**输出字段：**
```json
{
  "building_name": "物件名称",
  "url": "详情页链接",
  "price": "2590万円",
  "area": "34.09m2（10.31坪）",
  "layout": "1LDK",
  "age": "1979年2月",
  "address": "東京都墨田区千歳１-1-8",
  "details": {...}
}
```

**可修改配置：**

在 `suumo_scraper.py` 的 `main()` 函数中：

```python
# 修改区域
result = scrape_suumo_sale(station="錦糸町", max_pages=3)

# 修改搜索URL（第67-74行）
# sc=13107: 墨田区
# 可以改为其他区的代码
```

**支持的页面类型：**
1. 买房页面（中古マンション）- 当前配置
2. 租房页面（賃貸） - 需修改URL

**特点：**
- 自动识别页面类型并适配提取逻辑
- 提取完整的房源信息（价格、面积、户型、年限）
- 包含详情页链接
- 反爬虫机制
- 可配置无头模式

---

## 📊 数据导出脚本

### export_to_csv.py - JSON转CSV

**功能：** 将Suumo抓取的JSON数据转换为CSV格式，方便导入Google Sheets。

**使用方法：**
```bash
python3 scripts/export_to_csv.py
```

**输出文件：** `kinshicho_sale.csv`

**CSV包含的列：**
- 序号
- 物件名称
- 价格(万円)
- 单价(円/m²)
- 面积
- 面积(m²)
- 户型
- 建造年份
- 房龄(年)
- 地址
- 链接

**导入Google Sheets步骤：**
1. 打开 Google Sheets
2. 文件 → 导入 → 上传
3. 选择生成的CSV文件
4. 选择导入位置

---

### upload_to_gsheets.py - 直接上传到Google Sheets

**功能：** 直接通过API上传数据到Google Sheets（需要API认证）。

**前置要求：**
1. Google Cloud项目
2. 启用Google Sheets API
3. 服务账号JSON密钥（保存为`credentials.json`）

**使用方法：**
```bash
python3 scripts/upload_to_gsheets.py
```

**输出：** 创建或更新Google Sheets表格，并返回表格链接。

---

## 🗄️ 数据库脚本

### mysql_login.sh - MySQL登录

**功能：** 快速登录MySQL数据库。

**使用方法：**
```bash
./scripts/mysql_login.sh
```

**配置：**
- 用户名: root
- 密码: 123456
- 主机: 127.0.0.1
- 端口: 3306

---

## 🔄 自动化运行

### 定时任务（Crontab）

**每天早上9点采集股票数据：**
```bash
0 9 * * * cd /path/to/skynet && source venv/bin/activate && python3 scripts/stock_indices.py
```

**每天早上9点半采集PE比率：**
```bash
30 9 * * * cd /path/to/skynet && source venv/bin/activate && python3 scripts/nasdaq_pe.py
```

### n8n工作流

脚本设计为兼容n8n的Execute Command节点，可以：
1. 在n8n中创建Workflow
2. 使用Execute Command节点运行Python脚本
3. 解析JSON输出并处理
4. 发送通知或触发其他操作

---

## ⚠️ 注意事项

### 爬虫使用注意

1. **遵守网站robots.txt**
2. **合理设置抓取频率**（建议间隔2-3秒）
3. **不要过度抓取**（避免IP被封）
4. **仅用于个人学习和研究**

### 数据库连接

- 确保MySQL服务正在运行
- 检查防火墙设置
- 如果使用Docker，注意网络配置

### Chrome浏览器

- Selenium需要Chrome浏览器
- ChromeDriver会自动下载
- 首次运行可能较慢（下载driver）

---

## 📝 自定义配置

### 修改数据库连接

在各脚本中找到 `get_db_connection()` 函数：

```python
connection = pymysql.connect(
    host='localhost',      # 修改主机
    user='root',           # 修改用户名
    password='123456',     # 修改密码
    database='finances',   # 修改数据库名
    charset='utf8mb4'
)
```

### 修改Suumo搜索条件

在 `suumo_scraper.py` 中：

```python
# 修改区域代码
sc=13107  # 墨田区
# 其他区的代码可以从Suumo网站的URL中获取

# 修改类型
bs=011   # 中古マンション（二手公寓）
bs=040   # 賃貸（租房）
```

---

## 🐛 调试技巧

### 查看详细日志

```bash
python3 scripts/nasdaq_pe.py 2>&1 | tee debug.log
```

### 测试Selenium

```python
# 取消headless模式查看浏览器操作
chrome_options.add_argument("--headless")  # 注释掉这行
```

### 检查数据库

```bash
./scripts/mysql_login.sh
# 然后执行SQL查询
SELECT * FROM stock_indices ORDER BY date DESC LIMIT 5;
```

