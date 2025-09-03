#!/usr/bin/env python
#coding:utf-8

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configs.config import mail_config

class MailSender:
    def __init__(self):
        self.username = mail_config["username"]
        self.password = mail_config["password"]
        self.smtp_server = mail_config["smtp_server"]
        self.smtp_port = mail_config["smtp_port"]

    def send_email(self, receivers, subject, body):
        """
        发送邮件
        :param receivers: 收件人列表 (list)
        :param subject: 邮件主题
        :param body: 邮件正文
        """
        # 构建邮件
        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = ", ".join(receivers)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, receivers, msg.as_string())
            server.quit()
            print("✅ 邮件发送成功！")
        except Exception as e:
            print("❌ 发送失败:", e)


if __name__ == "__main__":
    # 使用示例
    sender = MailSender()
    sender.send_email(
        receivers=["liyuanhua0512@outlook.com"],
        subject="测试邮件（面向对象）",
        body="你好，这是一封测试邮件（来自Python类）。"
    )
