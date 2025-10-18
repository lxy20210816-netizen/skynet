# 雪球爬虫登录指南

## 🔐 为什么需要登录？

雪球网站**需要登录**才能查看用户的完整发文内容。未登录用户只能看到部分公开信息。

## 📝 快速配置（3步）

### 步骤1：创建登录配置文件

```bash
cd ~/Desktop/workspace/skynet/config
cp xueqiu_login.json.example xueqiu_login.json
```

### 步骤2：编辑配置文件

编辑 `config/xueqiu_login.json`，填入你的雪球账号：

```json
{
  "phone": "138xxxxxxxx",
  "password": "你的密码"
}
```

### 步骤3：运行爬虫

```bash
cd ~/Desktop/workspace/skynet
./scripts/sync_xueqiu.sh
```

## 🚀 使用方法

### 方式一：使用配置文件（推荐）

配置好 `xueqiu_login.json` 后，直接运行：

```bash
python3 scripts/xueqiu_with_login.py --user-id 9528875558
```

### 方式二：命令行参数

不创建配置文件，直接在命令行提供账号密码：

```bash
python3 scripts/xueqiu_with_login.py \
    --user-id 9528875558 \
    --phone "138xxxxxxxx" \
    --password "你的密码" \
    --visible
```

### 方式三：使用保存的Cookies

首次登录成功后，cookies会自动保存到 `config/xueqiu_cookies.json`

下次运行时会自动使用保存的cookies，无需重新登录：

```bash
python3 scripts/xueqiu_with_login.py --user-id 9528875558
```

如果cookies过期，会自动提示重新登录。

## 📋 命令参数

| 参数 | 说明 | 必填 |
|------|------|------|
| `--user-id` | 雪球用户ID | 是 |
| `--max-posts` | 最多抓取的发文数 | 否（默认20） |
| `--phone` | 登录手机号 | 否（可从配置文件读取） |
| `--password` | 登录密码 | 否（可从配置文件读取） |
| `--visible` | 显示浏览器窗口 | 否 |
| `--force-login` | 强制重新登录 | 否 |
| `--output` | 输出文件路径 | 否 |
| `--format` | 输出格式（json/markdown/both） | 否 |

## 🔧 完整示例

### 示例1：首次使用（配置文件方式）

```bash
# 1. 创建配置文件
echo '{
  "phone": "138xxxxxxxx",
  "password": "yourpassword"
}' > config/xueqiu_login.json

# 2. 运行爬虫（显示浏览器）
python3 scripts/xueqiu_with_login.py \
    --user-id 9528875558 \
    --max-posts 30 \
    --visible

# 3. 首次登录成功后，cookies会被保存
# 4. 下次运行无需登录，cookies自动使用
```

### 示例2：使用命令行参数

```bash
# 不保存配置文件，直接提供账号密码
python3 scripts/xueqiu_with_login.py \
    --user-id 9528875558 \
    --phone "138xxxxxxxx" \
    --password "yourpassword" \
    --max-posts 50 \
    --output output/duanyongping.json
```

### 示例3：强制重新登录

```bash
# 当cookies过期或需要更换账号时
python3 scripts/xueqiu_with_login.py \
    --user-id 9528875558 \
    --force-login \
    --visible
```

### 示例4：一键运行脚本

```bash
# 使用Shell脚本（需要先配置xueqiu_login.json）
./scripts/sync_xueqiu.sh
```

## ⚠️ 注意事项

1. **安全提醒**
   - 配置文件包含敏感信息，**不要提交到Git**
   - `xueqiu_login.json` 已在 `.gitignore` 中排除
   - 建议使用小号或专门的测试账号

2. **验证码处理**
   - 如果登录需要验证码，脚本会暂停60秒
   - 使用 `--visible` 参数手动完成验证码输入
   - 验证完成后脚本会自动继续

3. **Cookies管理**
   - Cookies保存在 `config/xueqiu_cookies.json`
   - 有效期通常为几天到几周
   - 过期后会自动提示重新登录

4. **反爬虫限制**
   - 不要频繁抓取，建议间隔至少几分钟
   - 单次不要抓取过多发文（建议≤100条）
   - 如被限制，等待一段时间后再试

## 🐛 故障排除

### 问题1：登录失败

**可能原因**：
- 账号密码错误
- 需要验证码
- 页面结构变化

**解决方法**：
```bash
# 使用可见模式观察登录过程
python3 scripts/xueqiu_with_login.py \
    --user-id 9528875558 \
    --force-login \
    --visible
```

### 问题2：找不到配置文件

```bash
# 检查配置文件是否存在
ls -la config/xueqiu_login.json

# 如果不存在，从模板创建
cp config/xueqiu_login.json.example config/xueqiu_login.json
```

### 问题3：Cookies过期

```bash
# 删除旧cookies，强制重新登录
rm config/xueqiu_cookies.json
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --visible
```

### 问题4：仍然找不到发文

**可能原因**：
- 页面选择器变化
- 用户确实没有公开发文

**解决方法**：
```bash
# 1. 用可见模式查看页面
python3 scripts/xueqiu_with_login.py --user-id 9528875558 --visible

# 2. 确认用户ID是否正确
# 访问 https://xueqiu.com/u/9528875558 确认

# 3. 如果是段永平，他在2025年4月已暂停发文
# 但历史发文应该还在
```

## 📂 文件结构

```
skynet/
├── config/
│   ├── xueqiu_login.json          # 登录配置（需要创建）
│   ├── xueqiu_login.json.example  # 配置模板
│   └── xueqiu_cookies.json        # 保存的cookies（自动生成）
├── scripts/
│   ├── xueqiu_with_login.py       # 支持登录的爬虫
│   └── sync_xueqiu.sh             # 一键运行脚本
└── output/
    ├── xueqiu_duanyongping.json   # 抓取结果（JSON）
    └── xueqiu_duanyongping.md     # 抓取结果（Markdown）
```

## 🔗 相关资源

- 雪球官网：https://xueqiu.com
- 段永平主页：https://xueqiu.com/u/9528875558
- 项目文档：`/Documents/XUEQIU_USAGE.md`

## ⚡ 快速上手

最快的使用方式：

```bash
# 1. 创建登录配置
cat > config/xueqiu_login.json << EOF
{
  "phone": "你的手机号",
  "password": "你的密码"
}
EOF

# 2. 运行
./scripts/sync_xueqiu.sh

# 3. 查看结果
open output/xueqiu_duanyongping.md
```

完成！🎉

