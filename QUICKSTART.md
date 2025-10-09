# ⚡ 快速入门指南

5分钟快速上手Skynet数据采集系统！

## 🎯 第一步：环境准备（2分钟）

```bash
# 1. 进入项目目录
cd skynet

# 2. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

## 🗄️ 第二步：启动MySQL（1分钟）

```bash
# 使用Docker一键启动
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=finances \
  -p 3306:3306 \
  mysql:8.0

# 等待10秒让MySQL启动完成
sleep 10
```

## 📊 第三步：采集数据（2分钟）

### 采集股票数据

```bash
# 采集股票指数
python3 scripts/stock_indices.py

# 采集PE比率
python3 scripts/nasdaq_pe.py
```

看到 `"database_saved": true` 就表示成功！

### 采集房源数据

```bash
# 抓取锦糸町房源
python3 scripts/suumo_scraper.py > output/房源.json 2>&1

# 转换为CSV（可导入Excel/Google Sheets）
python3 scripts/export_to_csv.py
```

## ✅ 验证结果

### 查看数据库

```bash
./scripts/mysql_login.sh
```

然后执行SQL：
```sql
-- 查看最新的股票数据
SELECT * FROM stock_indices ORDER BY date DESC LIMIT 5;

-- 退出
exit;
```

### 查看输出文件

```bash
# 查看房源CSV
cat output/kinshicho_sale.csv | head -5

# 查看JSON数据
cat output/房源.json | jq '.data.total_properties'
```

## 🎉 完成！

现在您已经：
- ✅ 成功采集了股票数据
- ✅ 成功采集了房源数据
- ✅ 数据已保存到数据库和文件

## 📚 下一步

- 📖 阅读 [完整文档](README.md)
- 🔧 查看 [脚本说明](Documents/SCRIPTS.md)
- 🏗️ 了解 [项目架构](Documents/PROJECT_OVERVIEW.md)
- ⚙️ 配置 [定时任务](Documents/SCRIPTS.md#自动化运行)

## 🆘 遇到问题？

常见问题解决：

**问题1: pip安装失败**
```bash
# 升级pip
pip install --upgrade pip
```

**问题2: MySQL连接失败**
```bash
# 检查MySQL是否运行
docker ps | grep mysql

# 重启MySQL
docker restart mysql
```

**问题3: Chrome驱动下载慢**
```bash
# 等待首次下载完成（约1-2分钟）
# 或配置代理
export HTTP_PROXY=http://your-proxy:port
```

## 💡 提示

- 首次运行Selenium脚本会下载ChromeDriver，需要1-2分钟
- 股票数据每天运行一次即可
- 房源数据建议每周运行一次，避免过度抓取
- 所有JSON输出都可以用 `jq` 命令美化查看

---

**享受数据采集的乐趣！** 🚀

