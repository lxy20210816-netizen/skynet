# Config 配置目录

本目录存放项目的配置文件和凭证。

## 📁 目录内容

### credentials.json (必需)

Google Sheets API的服务账号凭证文件。

**获取方法：**
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用Google Sheets API
3. 创建服务账号并下载JSON密钥
4. 将文件放到此目录，命名为 `credentials.json`

**文件格式：**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "xxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "your-service-account@project.iam.gserviceaccount.com",
  ...
}
```

### 其他配置文件（可选）

您可以在此目录添加其他配置文件：
- `database.json` - 数据库配置
- `api_keys.json` - API密钥
- `settings.json` - 项目设置

## ⚠️ 安全提示

1. **不要提交到Git**
   - 此目录中的敏感文件已在 `.gitignore` 中被忽略
   - 只有 `.gitkeep` 和 `README.md` 会被跟踪

2. **保护凭证文件**
   ```bash
   chmod 600 config/credentials.json
   ```

3. **备份凭证**
   - 将凭证文件备份到安全位置
   - 不要通过聊天、邮件等方式分享

## 📖 相关文档

- [Google Sheets集成指南](../Documents/GOOGLE_SHEETS.md)
- [环境配置](../Documents/SETUP.md)

