# 📁 项目目录结构

清晰的项目组织结构说明。

```
skynet/
│
├── 📄 README.md                    # 项目主页（英文）
├── 📄 README_ZH.md                 # 项目主页（中文）  
├── 📄 QUICKSTART.md                # 5分钟快速入门指南
├── 📄 STRUCTURE.md                 # 本文档 - 项目结构说明
├── 📄 requirements.txt             # Python依赖包列表
├── 📄 .gitignore                   # Git忽略规则
│
├── 📁 config/                      # 配置文件目录 🔒
│   ├── credentials.json            # Google API凭证（不提交到Git）
│   └── README.md                   # 配置说明
│
├── 📁 scripts/                     # 核心脚本目录 ⚙️
│   ├── README.md                   # 脚本使用说明
│   │
│   ├── 📈 金融数据采集
│   │   ├── nasdaq_pe.py            # 纳斯达克100 PE比率
│   │   └── stock_indices.py        # 股票指数数据
│   │
│   ├── 🏠 房地产数据采集
│   │   └── suumo_scraper.py        # Suumo房源爬虫
│   │
│   ├── 📊 数据导入导出
│   │   ├── export_to_csv.py        # JSON转CSV
│   │   ├── upload_to_gsheets.py    # 上传到Google Sheets
│   │   └── read_gsheets.py         # 从Google Sheets读取
│   │
│   ├── 🔧 工具脚本
│   │   ├── mysql_login.sh          # MySQL快速登录
│   │   └── example_read_gsheets.sh # 使用示例
│   │
│   └── 📝 脚本统计
│       ├── Python脚本: 6个
│       ├── Shell脚本: 2个
│       └── 总代码量: ~60KB
│
├── 📁 Documents/                   # 文档中心 📚
│   ├── PROJECT_OVERVIEW.md         # 项目架构设计
│   ├── SETUP.md                    # 环境配置指南
│   ├── SCRIPTS.md                  # 脚本详细手册
│   ├── GOOGLE_SHEETS.md            # Google Sheets集成
│   ├── db_config.md                # 数据库表结构
│   ├── mail_config.md              # 邮件配置
│   ├── rss.md                      # RSS配置
│   └── usage.md                    # n8n使用说明
│
├── 📁 output/                      # 输出结果目录 📤
│   ├── .gitkeep                    # 保留目录结构
│   ├── gsheet_data.json            # Google Sheets数据
│   ├── kinshicho_sale_final.json   # 房源JSON数据
│   └── kinshicho_sale.csv          # 房源CSV数据
│   
│   📝 说明: 此目录的数据文件不提交到Git
│
├── 📁 data/                        # 临时数据目录 💾
│   └── .gitkeep                    # 保留目录结构
│   
│   📝 说明: 用于存放临时数据，内容不提交到Git
│
└── 📁 venv/                        # Python虚拟环境 🐍
    ├── bin/                        # 可执行文件
    ├── lib/                        # 依赖包
    └── pyvenv.cfg                  # 环境配置
    
    📝 说明: 虚拟环境不提交到Git

```

## 📊 目录用途说明

### 🔒 config/ - 配置文件
- **用途**: 存放敏感配置文件
- **内容**: API凭证、密钥等
- **Git**: 内容被忽略，只保留结构
- **安全**: 设置权限 `chmod 600`

### ⚙️ scripts/ - 脚本代码
- **用途**: 所有数据采集和处理脚本
- **分类**: 按功能分为金融、房地产、工具等
- **Git**: 完全跟踪，这是项目的核心

### 📚 Documents/ - 文档中心
- **用途**: 项目文档和说明
- **内容**: 配置指南、使用手册、架构设计
- **Git**: 完全跟踪

### 📤 output/ - 输出结果
- **用途**: 存放脚本输出的数据文件
- **格式**: JSON、CSV等
- **Git**: 内容被忽略（数据文件不版本控制）

### 💾 data/ - 临时数据
- **用途**: 存放临时数据、缓存等
- **Git**: 内容被忽略

### 🐍 venv/ - 虚拟环境
- **用途**: Python依赖隔离
- **Git**: 完全忽略（通过requirements.txt管理）

## 📏 设计原则

### ✅ 清晰分离
- 代码 (scripts/)
- 数据 (output/, data/)
- 配置 (config/)
- 文档 (Documents/)

### ✅ 安全第一
- 敏感文件不提交
- 配置文件独立管理
- 环境变量支持

### ✅ 易于维护
- 每个目录有README
- 文件命名规范
- 功能模块化

## 📈 文件统计

```
总文件数: ~30个
├── Python脚本: 6个 (~60KB)
├── 文档文件: 11个 (~50KB)
├── 配置文件: 2个
└── 数据文件: 3个 (~26KB)
```

## 🎯 查找文件快速参考

| 我想... | 应该查看... |
|--------|-----------|
| 快速开始使用 | `QUICKSTART.md` |
| 了解项目架构 | `Documents/PROJECT_OVERVIEW.md` |
| 配置环境 | `Documents/SETUP.md` |
| 使用某个脚本 | `Documents/SCRIPTS.md` 或 `scripts/README.md` |
| 配置Google Sheets | `Documents/GOOGLE_SHEETS.md` |
| 查看数据库结构 | `Documents/db_config.md` |
| 修改脚本 | `scripts/` 目录 |
| 查看输出结果 | `output/` 目录 |

## 🔄 目录维护

### 清理临时文件
```bash
# 清理output目录中的旧文件
rm -f output/*.json output/*.csv

# 清理data目录
rm -rf data/*
```

### 备份重要数据
```bash
# 备份数据库
mysqldump -u root -p123456 finances > backup/db_$(date +%Y%m%d).sql

# 备份配置
cp config/credentials.json backup/
```

## 📝 Git版本控制

### 被跟踪的文件
- ✅ 所有脚本文件
- ✅ 所有文档文件
- ✅ requirements.txt
- ✅ .gitignore
- ✅ 目录结构（通过.gitkeep）

### 被忽略的内容
- ❌ venv/ (虚拟环境)
- ❌ config/*.json (敏感配置)
- ❌ output/* (输出数据)
- ❌ data/* (临时数据)
- ❌ __pycache__/ (Python缓存)
- ❌ .DS_Store (系统文件)

---

**保持项目整洁，结构清晰！** ✨

