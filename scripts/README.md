# Scripts 脚本说明

本目录包含所有数据采集和处理脚本。

## 📂 脚本列表

### 📈 金融数据采集

| 脚本 | 功能 | 数据源 | 输出 |
|-----|------|--------|------|
| `nasdaq_pe.py` | 纳斯达克100 PE比率 | GuruFocus | JSON + MySQL |
| `stock_indices.py` | 股票指数收盘价 | Yahoo Finance | JSON + MySQL |

### 🏠 房地产数据采集

| 脚本 | 功能 | 数据源 | 输出 |
|-----|------|--------|------|
| `suumo_scraper.py` | Suumo房源信息 | Suumo.jp | JSON |
| `export_to_csv.py` | JSON转CSV | 本地JSON | CSV文件 |
| `upload_to_gsheets.py` | 上传到Google Sheets | 本地JSON | Google Sheets |

### 🔧 工具脚本

| 脚本 | 功能 | 说明 |
|-----|------|------|
| `mysql_login.sh` | MySQL登录 | 快速连接数据库 |

## 🚀 快速使用

### 1. 采集股票数据

```bash
# 激活虚拟环境
source ../venv/bin/activate

# 采集股票指数
python3 stock_indices.py

# 采集PE比率
python3 nasdaq_pe.py
```

### 2. 采集房源数据

```bash
# 抓取Suumo房源（输出到文件）
python3 suumo_scraper.py > ../output/suumo_$(date +%Y%m%d).json 2>&1

# 转换为CSV
python3 export_to_csv.py

# 结果在 ../output/kinshicho_sale.csv
```

### 3. 数据库管理

```bash
# 登录MySQL
./mysql_login.sh

# 查询最新数据
# SELECT * FROM stock_indices ORDER BY date DESC LIMIT 10;
```

## 📊 数据流程

```
┌─────────────────┐
│  数据源网站      │
│ GuruFocus/YF    │
│ Suumo          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python脚本     │
│ *.py           │
└────────┬────────┘
         │
         ├─────────────┐
         ▼             ▼
┌──────────────┐  ┌──────────────┐
│  MySQL数据库  │  │  JSON/CSV    │
│  finances    │  │  output/     │
└──────────────┘  └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │Google Sheets │
                 └──────────────┘
```

## 🔧 配置说明

### 修改数据库连接

所有脚本中的数据库连接配置：

```python
host='localhost'
user='root'
password='123456'
database='finances'
```

可根据实际情况修改。

### 修改Suumo搜索条件

在 `suumo_scraper.py` 中修改URL参数：

```python
# 第72-74行
base_url = "https://suumo.jp/jj/bukken/ichiran/JJ012FC001/"
params = "?ar=030&bs=011&ta=13&sc=13107&..."

# sc参数: 区域代码
# sc=13107  墨田区
# sc=13113  渋谷区
# sc=13101  千代田区
# 等等...
```

## 📅 运行频率建议

### 股票数据
- **运行时间：** 每天早上9:00-10:00
- **频率：** 每天1次
- **原因：** 获取前一交易日收盘数据

### PE比率
- **运行时间：** 每天早上9:30
- **频率：** 每天1次
- **原因：** GuruFocus通常在美股收盘后更新

### 房源数据
- **运行时间：** 每周或每月
- **频率：** 根据需求
- **原因：** 房源更新不频繁，避免过度抓取

## ⚡ 性能优化

### 无头模式

所有Selenium脚本都支持无头模式，取消以下行的注释：

```python
chrome_options.add_argument("--headless")
```

### 并发运行

可以同时运行多个脚本：

```bash
# 后台运行
nohup python3 stock_indices.py > ../output/stock.log 2>&1 &
nohup python3 nasdaq_pe.py > ../output/pe.log 2>&1 &
```

## 🐛 调试模式

### 启用详细日志

```bash
# 保留所有输出
python3 suumo_scraper.py 2>&1 | tee debug.log

# 只看关键信息
python3 suumo_scraper.py 2>&1 | grep -E "(成功|失败|错误)"
```

### 测试模式

修改 `max_pages=1` 来减少抓取量进行测试。

## 📦 依赖管理

### 查看已安装包

```bash
source ../venv/bin/activate
pip list
```

### 导出依赖列表

```bash
pip freeze > requirements.txt
```

### 安装所有依赖

```bash
pip install -r requirements.txt
```

## 🆘 常见错误处理

### 错误1: 数据库连接失败

```
数据库连接失败: (2003, "Can't connect to MySQL server...")
```

**解决方案：**
1. 检查MySQL是否运行：`docker ps` 或 `systemctl status mysql`
2. 检查端口：`netstat -an | grep 3306`
3. 检查密码是否正确

### 错误2: Selenium超时

```
Message: timeout: Timed out receiving message from renderer
```

**解决方案：**
1. 增加等待时间：`WebDriverWait(driver, 30)`
2. 检查网络连接
3. 更新Chrome浏览器

### 错误3: ChromeDriver版本不匹配

```
This version of ChromeDriver only supports Chrome version XX
```

**解决方案：**
- 更新Chrome浏览器到最新版本
- 或清除缓存：`rm -rf ~/.wdm`

## 📞 获取帮助

详细配置请参考：[../Documents/SETUP.md](../Documents/SETUP.md)

