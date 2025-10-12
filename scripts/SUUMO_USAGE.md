# Suumo爬虫使用指南

## 功能介绍

`suumo_scraper.py` 是一个强大的Suumo房产信息爬虫，支持：
- 🏠 抓取锦糸町附近的二手公寓信息
- 📊 自动上传到Google Sheets
- 💾 保存数据到本地JSON文件
- 🎨 美化的表格格式（带emoji表头、数字格式化、边框等）

## 快速开始

### 1. 基础使用（只抓取，不上传）

```bash
# 抓取3页数据（默认）
python3 scripts/suumo_scraper.py

# 抓取5页数据
python3 scripts/suumo_scraper.py --max-pages 5
```

### 2. 抓取并上传到Google Sheets ⭐

```bash
# 抓取并自动上传到预设的Google表格（房地产池）
python3 scripts/suumo_scraper.py --upload

# 指定上传的页数
python3 scripts/suumo_scraper.py --upload --max-pages 5
```

### 3. 保存到本地文件

```bash
# 抓取并保存JSON
python3 scripts/suumo_scraper.py -o output/suumo_latest.json

# 抓取、保存JSON、并上传到Google Sheets
python3 scripts/suumo_scraper.py --upload -o output/suumo_latest.json
```

## 完整参数说明

```bash
python3 scripts/suumo_scraper.py [选项]

选项：
  --upload              抓取后自动上传到Google Sheets
  --sheet-id ID         Google Sheets ID（默认：1b55-D54NLbBo1yJd-OjDy7rqCBEkK8Dza3vDLZCPaiU）
  --worksheet NAME      工作表名称（默认：房地产池）
  --credentials PATH    Google API凭证文件路径（默认：config/credentials.json）
  --max-pages N         最大抓取页数（默认：3）
  --output, -o PATH     保存JSON到文件
  --help, -h            显示帮助信息
```

## Google Sheets配置

### 第一次使用前需要配置Google Sheets API

#### 1. 获取凭证文件

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用以下API：
   - Google Sheets API
   - Google Drive API
3. 创建服务账号并下载JSON密钥
4. 将密钥文件保存为 `config/credentials.json`

#### 2. 共享表格

1. 打开凭证文件 `config/credentials.json`
2. 复制服务账号邮箱（形如：`xxx@xxx.iam.gserviceaccount.com`）
3. 在Google Sheets中点击"共享"
4. 将表格共享给该邮箱，权限设为"编辑者"

详细配置说明请参考：[Documents/GOOGLE_SHEETS.md](../Documents/GOOGLE_SHEETS.md)

## 输出格式

### Google Sheets表头

上传到Google Sheets后，表格包含以下列：

| 列名 | 说明 | 格式 |
|------|------|------|
| 🔢 序号 | 房源序号 | 数字 |
| 🏢 物件名称 | 公寓/大楼名称 | 文本 |
| 💰 价格(万円) | 售价 | 千位分隔符 |
| 📊 单价(万円/m²) | 每平米单价 | 保留2位小数 |
| 📏 面积(m²) | 专有面积 | 保留2位小数 |
| 🏠 户型 | 如1LDK、2DK等 | 文本 |
| 📅 建造年份 | 建造年份 | 年份 |
| ⏳ 房龄(年) | 房龄 | 整数 |
| 📍 地址 | 详细地址 | 文本 |
| 🚇 交通 | 交通信息 | 文本 |
| 🔗 详情链接 | Suumo详情页 | URL |
| ⏰ 更新时间 | 数据更新时间 | YYYY-MM-DD HH:MM |

### 表格美化特性

- ✅ 表头冻结（滚动时表头始终可见）
- ✅ 表头蓝色背景 + 粗体
- ✅ 数字列右对齐
- ✅ 价格自动千位分隔符
- ✅ 所有单元格带边框
- ✅ 列宽自动调整
- ✅ 序号和年份居中对齐

## 使用示例

### 示例1：日常更新房源数据

```bash
# 每天运行一次，更新Google表格
python3 scripts/suumo_scraper.py --upload --max-pages 3
```

### 示例2：深度抓取并备份

```bash
# 抓取10页数据，同时保存到本地和Google Sheets
python3 scripts/suumo_scraper.py --upload --max-pages 10 -o output/suumo_$(date +%Y%m%d).json
```

### 示例3：使用不同的Google表格

```bash
# 上传到其他表格
python3 scripts/suumo_scraper.py --upload \
  --sheet-id "YOUR_SHEET_ID" \
  --worksheet "我的房源表"
```

### 示例4：定时任务（Crontab）

```bash
# 添加到crontab，每天早上8点自动更新
0 8 * * * cd /Users/a0000/Desktop/workspace/skynet && source venv/bin/activate && python3 scripts/suumo_scraper.py --upload --max-pages 5 2>&1 | logger -t suumo-scraper
```

## 数据说明

### 抓取来源
- **地区**：墨田区（锦糸町所在区）
- **类型**：二手公寓（中古マンション）
- **网站**：Suumo.jp

### 数据字段
- `building_name`: 物件名称
- `price`: 售价（万円）
- `area`: 专有面积（m²）
- `layout`: 户型（如1LDK、2DK）
- `age`: 建造年份信息
- `address`: 地址
- `access`: 交通信息（车站、步行时间）
- `url`: 详情链接

### 注意事项
⚠️ 列表页显示的是基本信息，详细信息需要访问各房源的详情链接

## 故障排除

### 问题1：浏览器启动失败

```
错误：启动浏览器失败
```

**解决方案：**
```bash
# 安装或更新Chrome浏览器
# macOS:
brew install --cask google-chrome

# 安装webdriver-manager
pip install webdriver-manager
```

### 问题2：无法上传到Google Sheets

```
错误：找不到凭证文件
```

**解决方案：**
1. 确保 `config/credentials.json` 存在
2. 检查文件权限：`chmod 600 config/credentials.json`
3. 参考 [Google Sheets配置](#google-sheets配置)

### 问题3：权限被拒绝

```
错误：PERMISSION_DENIED
```

**解决方案：**
1. 确认已将表格共享给服务账号邮箱
2. 确认权限为"编辑者"（不是"查看者"）
3. 等待1-2分钟让权限生效

### 问题4：抓取失败或数据不完整

```
错误：找不到房产信息
```

**解决方案：**
1. 检查网络连接
2. Suumo网站可能有反爬虫机制，尝试：
   - 减少抓取页数（`--max-pages 1`）
   - 等待几分钟后重试
3. 网站结构可能已更新，需要更新爬虫代码

## 进阶技巧

### 技巧1：结合jq处理JSON数据

```bash
# 抓取并筛选价格低于3000万円的房源
python3 scripts/suumo_scraper.py -o output/suumo.json
cat output/suumo.json | jq '.data.properties[] | select(.price | tonumber < 3000)'
```

### 技巧2：比较历史数据

```bash
# 每周保存一次快照
python3 scripts/suumo_scraper.py -o output/suumo_week_$(date +%U).json

# 比较差异
diff output/suumo_week_01.json output/suumo_week_02.json
```

### 技巧3：多地区抓取

修改脚本中的 `base_url` 和 `params` 可以抓取其他地区的数据。

## 相关文档

- [Google Sheets集成指南](../Documents/GOOGLE_SHEETS.md)
- [项目总览](../Documents/PROJECT_OVERVIEW.md)
- [脚本说明](README.md)

## 版本历史

### v2.0 (2025-10-11)
- ✨ 新增：自动上传到Google Sheets功能
- ✨ 新增：美化的表格格式（emoji、边框、格式化）
- ✨ 新增：命令行参数支持
- 🐛 修复：数据提取更准确
- 📝 完善：详细的使用文档

### v1.0 (之前)
- 基础爬虫功能
- JSON输出

## 支持

如有问题，请查看：
1. [故障排除](#故障排除)
2. [Google Sheets配置文档](../Documents/GOOGLE_SHEETS.md)
3. 项目Issues

---

**Happy Scraping! 🏠📊**

