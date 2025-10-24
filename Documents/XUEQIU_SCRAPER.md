# 雪球爬虫文档

## 📌 概述

雪球爬虫用于抓取雪球用户的发文内容。**雪球需要登录才能查看完整内容**，因此我们提供了支持登录的版本。

## 🎯 主要功能

- ✅ 自动登录雪球账号
- ✅ 保存和复用Cookies
- ✅ 抓取指定用户的发文
- ✅ 支持JSON和Markdown格式输出
- ✅ 提取点赞、评论、转发等互动数据

## 🚀 快速开始

### 1. 配置登录信息

```bash
cd ~/Desktop/workspace/skynet/config

# 从模板创建配置文件
cp xueqiu_login.json.example xueqiu_login.json

# 编辑配置文件，填入你的账号密码
nano xueqiu_login.json
```

配置文件格式：
```json
{
  "phone": "你的雪球登录手机号",
  "password": "你的密码"
}
```

### 2. 运行爬虫

#### 方式一：一键脚本（推荐）

```bash
cd ~/Desktop/workspace/skynet
./scripts/sync_xueqiu.sh
```

#### 方式二：Python脚本

```bash
cd ~/Desktop/workspace/skynet
source venv/bin/activate

# 抓取段永平的发文
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --max-posts 50
```

## 📚 可用脚本

| 脚本 | 说明 | 推荐 |
|------|------|------|
| `xueqiu_with_login.py` | **支持登录版本（推荐）** | ⭐⭐⭐⭐⭐ |
| `xueqiu_api.py` | API版本（需要登录，未完成） | ⭐⭐ |
| `xueqiu_scraper.py` | 基础版本（无登录，不可用） | ❌ |
| `sync_xueqiu.sh` | 一键运行脚本 | ⭐⭐⭐⭐⭐ |

**建议使用：`xueqiu_with_login.py`**

## 🛠️ 常用命令

### 抓取段永平的发文

```bash
# 默认抓取（使用配置文件中的账号）
python3 scripts/xueqiu_with_login.py --user-id 9528875558

# 显示浏览器窗口（首次使用推荐）
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --visible

# 抓取更多发文
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --max-posts 100

# 强制重新登录
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --force-login --visible
```

### 抓取其他用户

```bash
# 1. 先找到用户ID
# 访问 https://xueqiu.com 搜索用户
# 进入用户主页，URL格式：https://xueqiu.com/u/[USER_ID]

# 2. 使用用户ID抓取
python3 scripts/xueqiu_with_login.py --user-id [USER_ID] --max-posts 30
```

### 直接提供账号密码（不使用配置文件）

```bash
python3 scripts/xueqiu_with_login.py \
    --user-id 9528875558 \
    --phone "138xxxxxxxx" \
    --password "yourpassword" \
    --visible
```

## 📂 输出文件

抓取完成后，文件保存在 `output/` 目录：

- **JSON格式**：`xueqiu_duanyongping.json`
- **Markdown格式**：`xueqiu_duanyongping.md`

### JSON数据结构

```json
[
  {
    "id": "298765432",
    "user_id": "9528875558",
    "username": "大道无形我有型",
    "title": "投资思考...",
    "content": "完整内容...",
    "url": "https://xueqiu.com/9528875558/298765432",
    "published_at": "2024-12-01 10:30",
    "likes": "128",
    "comments": "45",
    "retweets": "23",
    "scraped_at": "2025-10-16T02:00:00"
  }
]
```

## ⚙️ 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--user-id` | 雪球用户ID | 9528875558（段永平） |
| `--max-posts` | 最多抓取的发文数 | 20 |
| `--phone` | 登录手机号 | 从配置文件读取 |
| `--password` | 登录密码 | 从配置文件读取 |
| `--output` | 输出文件路径 | ../output/xueqiu_posts.json |
| `--format` | 输出格式 | both（json+markdown） |
| `--visible` | 显示浏览器窗口 | False |
| `--force-login` | 强制重新登录 | False |

## 🔐 Cookies管理

### 自动保存

首次登录成功后，cookies会自动保存到：
```
config/xueqiu_cookies.json
```

### 自动复用

下次运行时会自动使用保存的cookies，无需重新登录：
```bash
# 第一次：需要登录
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --visible

# 第二次及以后：自动使用cookies
python3 scripts/xueqiu_with_login.py --user-id 9528875558
```

### 手动清理

当cookies过期或需要更换账号时：
```bash
# 删除旧cookies
rm config/xueqiu_cookies.json

# 重新登录
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --force-login --visible
```

## ⚠️ 重要提示

### 1. 段永平已暂停发文

段永平（大道无形我有型）在 **2025年4月10日** 宣布暂时不再发雪球。

因此抓取的是**历史发文**，不会有新内容。

### 2. 安全注意事项

- ❗ **不要把 `xueqiu_login.json` 提交到Git**（已在.gitignore中排除）
- 建议使用小号或测试账号
- 定期更换密码

### 3. 反爬虫限制

- 不要频繁抓取（建议间隔≥5分钟）
- 单次不要抓取过多（建议≤100条）
- 如被限制，等待后再试

### 4. 验证码处理

如果登录需要验证码：
- 脚本会暂停60秒
- 使用 `--visible` 参数手动完成验证
- 验证完成后脚本自动继续

## 🐛 故障排除

### 问题1：登录失败

```bash
# 使用可见模式查看登录过程
python3 scripts/xueqiu_with_login.py \
    --user-id 9528875558 \
    --force-login \
    --visible
```

### 问题2：找不到发文

```bash
# 1. 确认用户ID正确
# 访问 https://xueqiu.com/u/9528875558

# 2. 使用可见模式观察页面
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --visible

# 3. 检查是否登录成功
ls -la config/xueqiu_cookies.json
```

### 问题3：Cookies过期

```bash
# 强制重新登录
python3 scripts/xueqiu_with_login.py \
    --user-id 9528875558 \
    --force-login \
    --visible
```

### 问题4：页面元素找不到

可能是雪球页面结构更新了，需要更新CSS选择器。

使用可见模式观察页面元素：
```bash
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --visible
```

## 📖 详细文档

- **登录配置指南**：`scripts/XUEQIU_LOGIN_GUIDE.md`
- **使用说明**：`Documents/XUEQIU_USAGE.md`
- **快速上手**：`scripts/README_XUEQIU.md`

## 🔗 相关链接

- 雪球官网：https://xueqiu.com
- 段永平主页：https://xueqiu.com/u/9528875558
- 项目主文档：`Documents/PROJECT_OVERVIEW.md`

## 💡 示例：完整工作流

```bash
# 步骤1：配置登录信息
cat > config/xueqiu_login.json << EOF
{
  "phone": "138xxxxxxxx",
  "password": "yourpassword"
}
EOF

# 步骤2：首次运行（显示浏览器）
python3 scripts/xueqiu_with_login.py \
    --user-id 9528875558 \
    --max-posts 50 \
    --visible

# 步骤3：查看结果
cat output/xueqiu_posts.json | jq '.[0]'  # 查看第一条
open output/xueqiu_posts.md              # 用Markdown查看器打开

# 步骤4：后续使用（自动使用cookies）
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --max-posts 100

# 步骤5：定期更新
./scripts/sync_xueqiu.sh
```

---

**提示**：首次使用建议加上 `--visible` 参数，观察登录过程是否正常。登录成功后，cookies会被保存，后续可以无头模式运行。





