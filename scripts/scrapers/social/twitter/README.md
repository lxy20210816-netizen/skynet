# Twitter 爬虫

Twitter数据抓取工具集合。

## 📚 脚本说明

### twitter_selenium.py
Twitter爬虫主脚本，使用Selenium抓取Twitter数据。

### twitter_save_cookies.py
保存Twitter登录Cookie，方便下次免登录使用。

### twitter_check.py
检查Twitter登录状态。

## 🚀 使用方法

### 保存登录Cookie
```bash
python3 twitter_save_cookies.py
```

### 检查登录状态
```bash
python3 twitter_check.py
```

### 抓取Twitter数据
```bash
python3 twitter_selenium.py
```

## 📝 配置

配置文件位置:
- 登录信息: `~/Desktop/workspace/skynet/config/twitter_login.json`
- Cookies: `~/Desktop/workspace/skynet/config/twitter_cookies.json`

## ⚠️ 注意事项

- Twitter有严格的反爬虫机制，请合理控制频率
- 建议使用小号进行测试
- Cookie会过期，需要定期更新

