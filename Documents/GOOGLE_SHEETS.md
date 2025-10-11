# Google Sheets 集成指南

本文档说明如何与Google Sheets集成，实现数据的读取和写入。

## 📋 前置准备

### 1. 创建Google Cloud项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 点击"启用API和服务"

### 2. 启用必要的API

启用以下API：
- ✅ Google Sheets API
- ✅ Google Drive API

### 3. 创建服务账号

1. 导航到 **IAM和管理 → 服务账号**
2. 点击 **创建服务账号**
3. 输入名称（例如：skynet-sheets）
4. 点击 **创建并继续**
5. 选择角色：**编辑者**（或自定义权限）
6. 点击 **完成**

### 4. 下载凭证文件

1. 点击创建的服务账号
2. 切换到 **密钥** 标签
3. 点击 **添加密钥 → 创建新密钥**
4. 选择 **JSON** 格式
5. 下载文件并重命名为 `credentials.json`
6. 将文件放到项目根目录

### 5. 共享Google Sheets

在凭证文件中找到服务账号邮箱（类似于：`skynet-sheets@项目ID.iam.gserviceaccount.com`）

然后在Google Sheets中：
1. 打开您的表格
2. 点击 **共享**
3. 输入服务账号邮箱
4. 选择权限：**查看者**（读取）或 **编辑者**（读写）
5. 点击 **发送**

## 📖 使用说明

### 读取Google Sheets数据

#### 基本用法

```bash
# 通过Sheet ID读取
python3 scripts/read_gsheets.py "1ABC...XYZ"

# 通过完整URL读取
python3 scripts/read_gsheets.py "https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit"

# 保存到文件
python3 scripts/read_gsheets.py "SHEET_ID" -o output/data.json
```

#### 高级用法

```bash
# 读取指定工作表（第2个工作表）
python3 scripts/read_gsheets.py "SHEET_ID" -w 1

# 读取指定范围
python3 scripts/read_gsheets.py "SHEET_ID" -r "A1:D10"

# 使用自定义凭证文件
python3 scripts/read_gsheets.py "SHEET_ID" -c /path/to/credentials.json
```

### 写入数据到Google Sheets

#### 上传Suumo数据

```bash
# 首先确保有JSON数据
python3 scripts/suumo_scraper.py > output/suumo.json 2>&1

# 上传到Google Sheets
python3 scripts/upload_to_gsheets.py
```

## 📊 示例场景

### 场景1: 读取投资组合

```bash
# 读取您的投资组合表格
python3 scripts/read_gsheets.py "YOUR_SHEET_ID" > portfolio.json

# 解析数据
cat portfolio.json | jq '.data.records[] | {股票代码: .["股票代码"], 持仓数量: .["数量"]}'
```

### 场景2: 读取房源追踪表

```bash
# 读取房源追踪表
python3 scripts/read_gsheets.py "YOUR_SHEET_ID" -w 0 > tracking.json

# 查看总数
cat tracking.json | jq '.data.rows'
```

### 场景3: 定期同步数据

```bash
# 读取Google Sheets数据
python3 scripts/read_gsheets.py "SHEET_ID" -o data/gsheet_data.json

# 处理数据（您的自定义脚本）
python3 scripts/process_data.py data/gsheet_data.json

# 结果写回数据库
python3 scripts/save_to_db.py data/processed_data.json
```

## 📝 输出格式

### 完整读取输出

```json
{
  "success": true,
  "data": {
    "spreadsheet_title": "我的表格",
    "spreadsheet_url": "https://docs.google.com/spreadsheets/d/...",
    "worksheet_title": "Sheet1",
    "rows": 100,
    "columns": 5,
    "headers": ["列1", "列2", "列3", "列4", "列5"],
    "records": [
      {
        "列1": "值1",
        "列2": "值2",
        "列3": "值3",
        "列4": "值4",
        "列5": "值5"
      },
      ...
    ]
  }
}
```

### 范围读取输出

```json
{
  "success": true,
  "data": {
    "range": "A1:D10",
    "values": [
      ["A1", "B1", "C1", "D1"],
      ["A2", "B2", "C2", "D2"],
      ...
    ]
  }
}
```

## 🔐 安全建议

### 保护凭证文件

```bash
# 设置文件权限（仅所有者可读）
chmod 600 credentials.json

# 确保不会提交到Git
# credentials.json 已在 .gitignore 中
```

### 服务账号权限

建议：
- ✅ 使用**只读**权限（如果只需读取）
- ✅ 为不同用途创建不同的服务账号
- ❌ 不要使用个人账号的凭证

## 🐛 故障排除

### 错误1: 找不到凭证文件

```
FileNotFoundError: credentials.json
```

**解决：** 确保 `credentials.json` 在项目根目录，或使用 `-c` 参数指定路径。

### 错误2: 权限被拒绝

```
gspread.exceptions.APIError: PERMISSION_DENIED
```

**解决：** 
1. 检查是否已与服务账号邮箱共享表格
2. 确认共享权限是否足够（至少需要查看权限）

### 错误3: 找不到表格

```
gspread.exceptions.SpreadsheetNotFound
```

**解决：**
1. 检查Sheet ID是否正确
2. 确认已共享表格给服务账号
3. 检查表格是否被删除或移动

### 错误4: API配额超限

```
APIError: RESOURCE_EXHAUSTED
```

**解决：**
- Google Sheets API有配额限制
- 默认：每分钟60次读取，60次写入
- 减少请求频率或申请配额增加

## 💡 使用技巧

### 1. 批量读取多个工作表

```bash
# 读取第一个工作表
python3 scripts/read_gsheets.py "SHEET_ID" -w 0 -o sheet1.json

# 读取第二个工作表
python3 scripts/read_gsheets.py "SHEET_ID" -w 1 -o sheet2.json
```

### 2. 结合jq处理数据

```bash
# 读取并筛选特定条件的数据
python3 scripts/read_gsheets.py "SHEET_ID" | \
  jq '.data.records[] | select(.价格 | tonumber > 3000)'
```

### 3. 定时同步

```bash
# 添加到crontab
0 */6 * * * cd /path/to/skynet && source venv/bin/activate && \
  python3 scripts/read_gsheets.py "SHEET_ID" -o data/latest.json
```

## 🔄 完整工作流示例

### 从Google Sheets读取 → 处理 → 保存到MySQL

```bash
#!/bin/bash
# sync_from_gsheets.sh

# 1. 读取Google Sheets
python3 scripts/read_gsheets.py "YOUR_SHEET_ID" -o data/gsheet.json

# 2. 解析并处理数据
python3 << 'EOF'
import json
import pymysql

# 读取数据
with open('data/gsheet.json', 'r') as f:
    data = json.load(f)

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='finances'
)

# 处理并保存数据
# ... 您的业务逻辑 ...

conn.close()
EOF

echo "✅ 同步完成"
```

## 📚 相关资源

- [gspread文档](https://docs.gspread.org/)
- [Google Sheets API文档](https://developers.google.com/sheets/api)
- [服务账号指南](https://cloud.google.com/iam/docs/service-accounts)

## ⚠️ 注意事项

1. **配额限制**
   - 每分钟最多60次读取请求
   - 不要在循环中频繁调用

2. **数据大小**
   - 单次读取建议不超过10000行
   - 大数据集建议分批读取

3. **凭证安全**
   - 不要将 `credentials.json` 提交到Git
   - 不要在公共场合分享凭证文件
   - 定期轮换服务账号密钥

