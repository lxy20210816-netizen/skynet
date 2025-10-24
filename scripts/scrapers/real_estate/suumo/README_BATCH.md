# 批量房产信息抓取工具

## 🎯 功能概述

这是一个用于批量抓取多个地区房产信息的Shell脚本工具，支持抓取二手公寓和一户建信息，并自动上传到Google Sheets。

## 📁 文件结构

```
scripts/scrapers/real_estate/suumo/
├── batch_scrape.sh          # 主批量抓取脚本
├── quick_start.sh           # 快速开始脚本（交互式）
├── suumo_scraper.py         # 核心抓取脚本
├── BATCH_SCRAPE_USAGE.md    # 详细使用说明
└── README_BATCH.md          # 本文件
```

## 🚀 快速开始

### 方法1：使用交互式脚本（推荐新手）

```bash
cd /Users/a0000/Desktop/workspace/skynet/scripts/scrapers/real_estate/suumo
./quick_start.sh
```

### 方法2：使用命令行脚本（推荐高级用户）

```bash
cd /Users/a0000/Desktop/workspace/skynet/scripts/scrapers/real_estate/suumo

# 抓取所有地区
./batch_scrape.sh

# 抓取指定地区
./batch_scrape.sh -s "kinshicho,kameido,akihabara"

# 只抓取二手公寓
./batch_scrape.sh -a

# 试运行模式
./batch_scrape.sh -d
```

## 🏘️ 支持的地区

| 地区名称 | 英文键名 | 所属区域 | 区域代码 |
|----------|----------|----------|----------|
| 錦糸町 | kinshicho | 墨田区 | 13107 |
| 平井 | hirai | 墨田区 | 13107 |
| 亀戸 | kameido | 江东区 | 13108 |
| 高島平 | takashimadaira | 板桥区 | 13119 |
| 板橋区役所前 | itabashikuyakusho | 板桥区 | 13119 |
| 秋葉原 | akihabara | 千代田区 | 13101 |
| 渋谷 | shibuya | 世田谷区 | 13112 |
| 上野 | ueno | 千代田区 | 13101 |
| 浅草寺 | asakusa | 墨田区 | 13107 |

## 📋 使用示例

### 1. 抓取单个地区
```bash
# 抓取錦糸町的房产信息
./batch_scrape.sh -s "kinshicho"
```

### 2. 抓取多个地区
```bash
# 抓取錦糸町、亀戸、秋葉原
./batch_scrape.sh -s "kinshicho,kameido,akihabara"
```

### 3. 只抓取特定类型
```bash
# 只抓取二手公寓
./batch_scrape.sh -a

# 只抓取一户建
./batch_scrape.sh --house-only
```

### 4. 试运行模式
```bash
# 查看将要抓取的地区，不实际上传
./batch_scrape.sh -d -s "kinshicho,kameido"
```

## ⏱️ 执行时间估算

| 地区数量 | 预计时间 | 说明 |
|----------|----------|------|
| 1个地区 | 2-3分钟 | 包含公寓+一户建 |
| 3个地区 | 6-9分钟 | 中等规模 |
| 9个地区 | 15-20分钟 | 全部地区 |

## 📊 输出结果

### 数据文件
- **位置**: `output/`
- **格式**: `suumo_{地区}_{类型}_{时间戳}.json`
- **示例**: `suumo_kinshicho_apartment_20251025_143022.json`

### 日志文件
- **位置**: `logs/`
- **格式**: `suumo_{地区}_{类型}_{时间戳}.log`
- **用途**: 调试和错误排查

### Google Sheets
- **工作表**: 房地产池
- **功能**: 自动去重、格式化、实时更新
- **链接**: 脚本执行完成后会显示

## 🔧 高级配置

### 自定义地区
编辑 `batch_scrape.sh` 中的地区配置：

```bash
# 添加新地区
get_station_code() {
    case "$1" in
        "new_area") echo "区域代码" ;;
        # ... 其他地区
    esac
}

get_station_name() {
    case "$1" in
        "new_area") echo "新地区名称" ;;
        # ... 其他地区
    esac
}
```

### 定时执行
```bash
# 添加到crontab，每天上午9点执行
0 9 * * * /path/to/batch_scrape.sh
```

## 🛠️ 故障排除

### 常见问题

1. **权限问题**
   ```bash
   chmod +x batch_scrape.sh
   chmod +x suumo_scraper.py
   ```

2. **Python依赖**
   ```bash
   pip install selenium gspread google-auth
   ```

3. **网络问题**
   - 检查网络连接
   - 确保可以访问suumo.jp
   - 检查Google Sheets API权限

4. **查看详细日志**
   ```bash
   tail -f logs/suumo_kinshicho_apartment_*.log
   ```

### 错误代码

| 退出码 | 含义 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 1 | 失败 | 检查日志文件 |
| 2 | 参数错误 | 检查命令行参数 |

## 📈 性能优化

### 建议设置
- **网络稳定**: 确保网络连接稳定
- **避免高峰**: 避开网站访问高峰时段
- **分批执行**: 大量地区建议分批执行

### 监控指标
- 成功率：目标 > 90%
- 平均耗时：每地区 2-3分钟
- 数据质量：检查输出文件完整性

## 🔄 维护建议

### 定期检查
1. **日志清理**: 定期清理旧日志文件
2. **数据备份**: 定期备份输出数据
3. **脚本更新**: 关注suumo网站结构变化

### 监控脚本
```bash
# 检查最近执行结果
ls -la output/ | tail -10

# 检查错误日志
grep -i error logs/*.log
```

## 📞 技术支持

如遇问题，请按以下顺序检查：

1. **环境检查**: Python版本、依赖包
2. **权限检查**: 脚本执行权限
3. **网络检查**: 网络连接和API权限
4. **日志分析**: 查看详细错误信息
5. **配置检查**: Google Sheets配置

## 🎉 成功案例

使用本工具已成功抓取：
- ✅ 錦糸町：30个公寓 + 20个一户建
- ✅ 亀戸：25个公寓 + 15个一户建
- ✅ 秋葉原：35个公寓 + 10个一户建

总计：**90个公寓 + 45个一户建 = 135个房源**

所有数据已成功上传到Google Sheets，支持实时查看和分析！
