# Skynet 项目概览

## 🎯 项目目标

Skynet是一个自动化数据采集和分析系统，主要用于：

1. **金融市场监控** - 追踪股票指数和市场指标
2. **房地产信息收集** - 采集日本房地产市场数据
3. **数据存储和分析** - 结构化存储并支持导出分析

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    数据采集层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │GuruFocus │  │Yahoo Fi. │  │  Suumo.jp   │          │
│  └─────┬────┘  └─────┬────┘  └──────┬───────┘          │
└────────┼─────────────┼──────────────┼──────────────────┘
         │             │              │
         ▼             ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                  Python脚本层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │nasdaq_pe │  │stock_idx │  │suumo_scraper│          │
│  └─────┬────┘  └─────┬────┘  └──────┬───────┘          │
└────────┼─────────────┼──────────────┼──────────────────┘
         │             │              │
         ▼             ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                    存储层                                │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  MySQL Database  │  │  JSON/CSV Files  │            │
│  │    finances      │  │     output/      │            │
│  └──────────────────┘  └─────────┬────────┘            │
└────────────────────────────────────┼──────────────────┘
                                     │
                                     ▼
                        ┌──────────────────────┐
                        │   Google Sheets      │
                        │   (可选导出)          │
                        └──────────────────────┘
```

## 📊 数据流说明

### 金融数据流

1. **采集** → `nasdaq_pe.py` / `stock_indices.py`
2. **解析** → 提取PE比率、收盘价等数据
3. **存储** → MySQL `finances.stock_indices` 表
4. **输出** → JSON格式（可对接n8n等工具）

### 房地产数据流

1. **采集** → `suumo_scraper.py` 爬取Suumo网站
2. **解析** → 提取价格、面积、户型等30+字段
3. **导出** → `export_to_csv.py` 转换为CSV
4. **上传** → `upload_to_gsheets.py` 上传到Google Sheets

## 🗂️ 目录说明

### /scripts - 核心脚本
所有数据采集和处理脚本，每个脚本独立运行。

### /Documents - 文档中心
- `SETUP.md` - 环境配置详细指南
- `SCRIPTS.md` - 脚本使用手册
- `db_config.md` - 数据库表结构
- `mail_config.md` - 邮件配置（n8n用）
- `rss.md` - RSS配置（n8n用）

### /output - 输出结果
存放所有输出的JSON、CSV文件（被git忽略）。

### /data - 临时数据
存放临时数据文件（被git忽略）。

### /venv - 虚拟环境
Python虚拟环境（被git忽略）。

## 💾 数据库设计

### stock_indices 表

存储股票指数的每日数据：

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | INT | 主键 |
| date | DATE | 交易日期（唯一） |
| nasdaq | DECIMAL | 纳斯达克综合指数 |
| nasdaq_100 | DECIMAL | 纳斯达克100指数 |
| nasdaq_100_pe | DECIMAL | 纳斯达克100 PE比率 |
| n225 | DECIMAL | 日经225指数 |
| vix | DECIMAL | VIX恐慌指数 |
| a | DECIMAL | 预留字段 |

**特点：**
- 按日期去重（UNIQUE KEY）
- 如果日期已存在则更新数据
- 支持部分字段更新

## 🔄 工作流程

### 日常数据更新流程

**每天早上执行：**

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 采集股票指数数据
python3 scripts/stock_indices.py

# 3. 采集PE比率
python3 scripts/nasdaq_pe.py

# 4. 查看数据库
./scripts/mysql_login.sh
# SELECT * FROM stock_indices ORDER BY date DESC LIMIT 5;
```

### 房源数据采集流程

**按需执行（每周或每月）：**

```bash
# 1. 采集Suumo房源
python3 scripts/suumo_scraper.py > output/suumo_$(date +%Y%m%d).json 2>&1

# 2. 转换为CSV
python3 scripts/export_to_csv.py

# 3. 导入Google Sheets
# 手动上传 output/kinshicho_sale.csv
# 或运行自动上传脚本（需配置credentials.json）
python3 scripts/upload_to_gsheets.py
```

## 🎯 使用场景

### 场景1: 股票投资参考

通过每日采集股票指数和PE比率数据，可以：
- 追踪市场趋势
- 分析估值水平
- 制定投资策略

### 场景2: 房产投资分析

通过采集房源信息，可以：
- 了解区域房价水平
- 对比不同房源的性价比
- 发现投资机会

### 场景3: n8n自动化

所有脚本输出JSON格式，可以：
- 在n8n中创建自动化工作流
- 定时采集数据
- 发送邮件通知
- 触发警报

## 🛠️ 扩展开发

### 添加新的数据源

1. 在 `scripts/` 目录创建新脚本
2. 参考现有脚本的结构
3. 输出JSON格式，包含 `success` 和 `data` 字段
4. 更新文档

### 添加新的数据库表

1. 在MySQL中创建表
2. 更新 `Documents/db_config.md`
3. 修改脚本添加写入逻辑

## 📈 未来规划

- [ ] 添加更多股票指数（S&P500、上证指数等）
- [ ] 支持更多房地产网站（Yahoo不动产、at-home等）
- [ ] 实现数据可视化Dashboard
- [ ] 添加价格预警功能
- [ ] 集成机器学习预测模型

## 🔒 安全建议

1. **不要提交敏感信息**
   - 数据库密码
   - API密钥
   - credentials.json

2. **定期备份数据库**
   ```bash
   mysqldump -u root -p finances > backup_$(date +%Y%m%d).sql
   ```

3. **合理使用爬虫**
   - 遵守网站robots.txt
   - 设置合理的抓取间隔
   - 不要过度请求

## 📚 参考资源

- [Selenium文档](https://selenium-python.readthedocs.io/)
- [yfinance文档](https://pypi.org/project/yfinance/)
- [n8n文档](https://docs.n8n.io/)
- [MySQL文档](https://dev.mysql.com/doc/)

