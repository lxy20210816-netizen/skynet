# Google Sheets数据导出工具

## 🎯 功能概述

这个工具可以从Google Sheets中读取房产数据，并导出到本地文件夹的多种格式文件中。

## 📁 文件结构

```
scripts/exporters/real_estate/
├── export_from_gsheets.py    # Python导出脚本
├── export_data.sh            # Shell执行脚本
└── README_EXPORT.md          # 本说明文档
```

## 🚀 快速使用

### 基本用法
```bash
cd /Users/a0000/Desktop/workspace/skynet/scripts/exporters/real_estate
./export_data.sh
```

### 自定义选项
```bash
# 导出到指定目录
./export_data.sh -d /path/to/your/folder

# 只导出JSON和CSV格式
./export_data.sh -f json,csv

# 指定不同的Google Sheets
./export_data.sh -s "your_sheet_id" -w "工作表名称"
```

## 📊 导出结果

### 文件格式
- **JSON**: 包含完整元数据的结构化数据
- **CSV**: Excel兼容的表格格式
- **Excel**: 格式化的.xlsx文件

### 输出目录
默认输出到：`/Users/a0000/Desktop/workspace/brain/skynet`

### 文件命名
- `real_estate_data_YYYYMMDD_HHMMSS.json`
- `real_estate_data_YYYYMMDD_HHMMSS.csv`
- `real_estate_data_YYYYMMDD_HHMMSS.xlsx`
- `data_summary_YYYYMMDD_HHMMSS.txt`

## 📈 数据统计

### 最新导出结果（2025-10-25）
- **总记录数**: 470条
- **地区分布**: 9个地区
- **类型分布**: 270个公寓 + 200个一户建
- **数据列数**: 14列

### 地区分布详情
| 地区 | 记录数 |
|------|--------|
| 錦糸町 | 100条 |
| 上野 | 50条 |
| 亀戸 | 50条 |
| 平井 | 50条 |
| 板橋区役所前 | 50条 |
| 浅草寺 | 50条 |
| 秋葉原 | 50条 |
| 高島平 | 50条 |
| 渋谷 | 20条 |

## 🔧 高级用法

### 命令行参数
```bash
./export_data.sh [选项]

选项:
  -h, --help              显示帮助信息
  -d, --dir DIR           指定输出目录
  -f, --formats FORMATS   指定导出格式
  -s, --sheet-id ID       指定Google Sheets ID
  -w, --worksheet NAME    指定工作表名称
```

### 支持的格式
- `json` - JSON格式（包含元数据）
- `csv` - CSV格式（Excel兼容）
- `excel` - Excel格式（.xlsx）

## 📋 数据字段

导出的数据包含以下字段：

1. 🗺️ **地区** - 房源所在地区
2. 🏘️ **类型** - 公寓/一户建
3. 🔢 **序号** - 数据序号
4. 🏢 **物件名称** - 房产名称
5. 💰 **价格(万円)** - 价格（万円）
6. 📊 **单价(万円/m²)** - 单价
7. 📏 **面积(m²)** - 建筑面积
8. 🏠 **户型** - 房间布局
9. 📅 **建造年份** - 建造年份
10. ⏳ **房龄(年)** - 房屋年龄
11. 📍 **地址** - 详细地址
12. 🚇 **交通** - 交通信息
13. 🔗 **详情链接** - 房源链接
14. ⏰ **更新时间** - 数据更新时间

## 🛠️ 故障排除

### 常见问题

1. **权限问题**
   ```bash
   chmod +x export_data.sh
   chmod +x export_from_gsheets.py
   ```

2. **Python依赖**
   ```bash
   pip3 install gspread google-auth pandas openpyxl
   ```

3. **Google Sheets权限**
   - 确保服务账号有读取权限
   - 检查凭证文件路径

4. **网络问题**
   - 检查网络连接
   - 确保可以访问Google Sheets API

### 错误代码
- **0**: 成功
- **1**: 失败（检查日志）

## 📞 技术支持

如遇问题，请检查：
1. Python环境和依赖包
2. Google Sheets API权限
3. 网络连接
4. 输出目录权限

## 🎉 成功案例

✅ **成功导出470条房产记录**
- 覆盖9个东京地区
- 包含公寓和一户建两种类型
- 支持多种格式导出
- 自动生成数据摘要

所有数据已成功保存到指定文件夹！
