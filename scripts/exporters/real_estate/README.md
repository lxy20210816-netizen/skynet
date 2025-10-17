# 不动产数据导出

导出不动产数据到Google Sheets和本地文件。

## 📚 脚本说明

### export_real_estate.py
不动产数据导出主脚本。

### sync_real_estate.sh
一键同步不动产数据的Shell脚本。

## 🚀 快速开始

```bash
# 运行同步脚本
./sync_real_estate.sh

# 或直接运行Python脚本
python3 export_real_estate.py
```

## 📂 输出位置

数据保存到: `/Users/a0000/Desktop/workspace/brain/skynet/`

## 🔄 定时任务

```bash
# 每周日晚上11点自动导出
0 23 * * 0 /Users/a0000/Desktop/workspace/skynet/scripts/exporters/real_estate/sync_real_estate.sh
```

