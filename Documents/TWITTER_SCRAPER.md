# Twitter推文抓取工具

## 📝 说明

使用Selenium浏览器自动化技术抓取Twitter公开推文，**无需API密钥**。

## 🚀 使用方法

### 基本用法

```bash
# 激活虚拟环境
cd ~/Desktop/workspace/skynet
source venv/bin/activate

# 获取指定用户的推文
python3 scripts/twitter_selenium.py 用户名 -n 推文数量 -o 输出文件
```

### 示例

```bash
# 获取Elon Musk的20条推文
python3 scripts/twitter_selenium.py elonmusk -n 20 \
  -o ~/Desktop/workspace/brain/musk_tweets.md

# 获取NVIDIA的50条推文
python3 scripts/twitter_selenium.py nvidia -n 50 \
  -o ~/Desktop/workspace/brain/nvidia_tweets.md

# 获取Bill Gates的推文
python3 scripts/twitter_selenium.py BillGates -n 30 \
  -o ~/Desktop/workspace/brain/gates_tweets.md

# 不指定输出路径（默认保存到output目录）
python3 scripts/twitter_selenium.py CNN -n 20
```

## 📋 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `username` | Twitter用户名（不含@） | `elonmusk` |
| `-n, --num` | 要获取的推文数量 | `-n 50` |
| `-o, --output` | 输出文件路径 | `-o output.md` |

## 📄 输出格式

### Markdown文件

```markdown
# 🐦 @nvidia 的推文
📅 获取时间：2025年10月13日 01:39
📊 推文数量：10 条

---

## 1. 2025-10-10 15:41
推文内容...

**互动数据**: ❤️ 257 点赞 | 🔄 41 转推 | 💬 24 回复

🔗 [查看原推文](链接)

---
```

### JSON文件

同时会生成JSON格式数据，包含：
- 推文ID
- 文本内容
- 发布时间
- 互动数据（点赞、转推、回复）
- 原推文链接

## 🎯 常用账号

### 科技公司
- `nvidia` - NVIDIA
- `Apple` - 苹果
- `Google` - 谷歌
- `Microsoft` - 微软
- `OpenAI` - OpenAI
- `Tesla` - 特斯拉

### 科技名人
- `elonmusk` - Elon Musk
- `BillGates` - Bill Gates
- `satyanadella` - 微软CEO
- `tim_cook` - 苹果CEO

### 新闻媒体
- `CNN` - CNN新闻
- `BBCWorld` - BBC
- `nytimes` - 纽约时报
- `WSJ` - 华尔街日报

## ⚙️ 技术特点

- ✅ **无需API密钥** - 使用浏览器自动化
- ✅ **无速率限制** - 不受Twitter API限制
- ✅ **自动去重** - 防止重复抓取
- ✅ **后台运行** - 无头浏览器模式
- ✅ **自动滚动** - 加载更多推文
- ✅ **完整数据** - 包含互动统计

## 📊 获取数据包含

每条推文包含：
- 📝 推文文本内容
- ⏰ 发布时间
- ❤️ 点赞数
- 🔄 转推数
- 💬 回复数
- 🔗 原推文链接

## ⚠️ 注意事项

1. **账号必须公开** - 无法获取私密账号的推文
2. **需要Chrome** - 确保系统已安装Chrome浏览器
3. **网络连接** - 需要能访问Twitter/X
4. **抓取速度** - 比API慢，但无限制

## 💡 提示

- 推文按时间从新到旧排序
- 默认保存到`output/`目录
- 同时生成`.md`和`.json`两种格式
- 可以重复运行获取最新推文

## 🆘 故障排除

### 问题1：无法启动浏览器
**解决**：确保已安装Chrome浏览器

### 问题2：获取的推文数量少于预期
**原因**：用户的推文较少，或页面加载问题
**解决**：正常现象，已获取用户所有可见推文

### 问题3：部分数据缺失
**原因**：Twitter页面结构变化
**解决**：脚本已自动处理缺失数据

## 📚 依赖

- Python 3.9+
- Selenium
- Chrome浏览器
- ChromeDriver（自动管理）

所有依赖已在`requirements.txt`中配置。

