# 房产数据去重功能说明

## 🎯 功能概述

为了解决Google Sheets中出现重复数据的问题，我已经增强了抓取脚本的去重功能，并提供了清理现有重复数据的工具。

## 🔧 增强的去重功能

### 多重去重检查
1. **复合键去重**：地区+类型+物件名称+URL
2. **URL去重**：检查房源链接是否重复
3. **名称+地区去重**：防止同一房源不同URL的重复

### 去重逻辑
```python
# 创建复合键
composite_key = f"{station_name}|{property_type_name}|{prop_name}|{prop_url}"

# 检查1: 复合键去重（最严格）
if composite_key in existing_records:
    is_duplicate = True
    duplicate_reason = "完全重复记录"

# 检查2: URL去重（如果URL有效）
elif prop_url != 'N/A' and prop_url in existing_urls:
    is_duplicate = True
    duplicate_reason = "URL重复"

# 检查3: 名称+地区去重（防止同一房源不同URL）
elif prop_name != 'N/A':
    name_region_key = f"{station_name}|{property_type_name}|{prop_name}"
    # 检查是否与现有记录重复
```

## 🧹 清理现有重复数据

### 使用清理脚本
```bash
cd /Users/a0000/Desktop/workspace/skynet/scripts/exporters/real_estate
python3 clean_duplicates.py
```

### 清理功能特点
- 🔍 **智能检测**：基于多个字段组合检测重复
- 📊 **详细统计**：显示原始记录数、重复记录数、唯一记录数
- ⚠️ **安全确认**：需要用户确认才会删除重复数据
- 🎨 **保持格式**：清理后保持表格格式和样式

## 🧪 测试去重功能

### 运行测试脚本
```bash
cd /Users/a0000/Desktop/workspace/skynet/scripts/scrapers/real_estate/suumo
./test_deduplication.sh
```

### 测试内容
1. **第1次抓取**：錦糸町公寓数据
2. **第2次抓取**：相同数据（应该被去重）
3. **第3次抓取**：不同地区数据（应该正常添加）

## 📊 去重效果

### 预期结果
- ✅ 相同房源不会重复添加
- ✅ 不同地区相同名称的房源可以共存
- ✅ 控制台显示跳过的重复记录
- ✅ 保持数据完整性

### 去重统计
```
📋 已有 470 个房源记录，将自动去重
📋 其中 450 个有有效URL
⏭️  跳过重复房源: 【即日案内!】頭金0円から購入可!ペット2匹OK×角部屋×【新宿/秋葉原】直通!... (完全重复记录)
```

## 🛠️ 使用方法

### 1. 清理现有重复数据
```bash
# 清理默认表格
python3 clean_duplicates.py

# 清理指定表格
python3 clean_duplicates.py --sheet-id "your_sheet_id" --worksheet "工作表名称"
```

### 2. 测试去重功能
```bash
# 运行测试脚本
./test_deduplication.sh
```

### 3. 正常抓取（自动去重）
```bash
# 批量抓取（自动去重）
./batch_scrape.sh

# 单个地区抓取（自动去重）
python3 suumo_scraper.py --upload --station "錦糸町" --append
```

## 🔍 去重检查项

### 检查字段
1. **地区** (列0): 房源所在地区
2. **类型** (列1): 公寓/一户建
3. **物件名称** (列3): 房产名称
4. **详情链接** (列12): 房源URL

### 去重规则
- **完全重复**：所有关键字段都相同
- **URL重复**：相同的房源链接
- **名称重复**：相同地区、类型、名称的房源

## 📈 性能优化

### 内存优化
- 使用集合(set)进行快速查找
- 避免重复的数据库查询
- 批量处理减少API调用

### 时间优化
- 预先加载现有数据
- 本地去重检查
- 减少网络请求

## 🚨 注意事项

### 安全提醒
1. **备份数据**：清理前建议备份重要数据
2. **确认操作**：清理脚本需要用户确认
3. **测试环境**：建议先在测试表格中验证

### 数据完整性
1. **保留最新**：重复记录保留最后添加的
2. **保持格式**：清理后保持表格格式
3. **统计准确**：提供详细的去重统计

## 🎉 预期效果

使用增强的去重功能后：
- ✅ **零重复**：新抓取的数据不会产生重复
- ✅ **智能识别**：准确识别各种类型的重复
- ✅ **高效处理**：快速处理大量数据
- ✅ **用户友好**：清晰的日志和统计信息

## 📞 技术支持

如遇问题，请检查：
1. Google Sheets API权限
2. 网络连接状态
3. 凭证文件路径
4. 工作表名称和格式

现在你的房产数据抓取系统已经具备了强大的去重功能，可以确保数据的唯一性和准确性！
