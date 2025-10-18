# 持仓数据导出

导出持仓数据到Google Sheets和本地文件。

## 📚 脚本说明

### export_holdings.py
持仓数据导出主脚本。

### sync_holdings.sh
一键同步持仓数据的Shell脚本。

## 🚀 快速开始

```bash
# 运行同步脚本
./sync_holdings.sh

# 或直接运行Python脚本
python3 export_holdings.py
```

## 📂 输出位置

数据保存到: `~/Desktop/workspace/brain/skynet/`

## 🔄 定时任务

```bash
# 每天晚上10点自动导出
0 22 * * * ~/Desktop/workspace/skynet/scripts/exporters/holdings/sync_holdings.sh
```

