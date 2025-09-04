#!/usr/bin/env python
#coding:utf-8

from openai import OpenAI
from configs.api_key_config import openai_api_key

# 初始化客户端
client = OpenAI(api_key=openai_api_key)

# 调用 ChatGPT
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "user", "content": "帮我写一个Python脚本，打印Hello World"}
    ]
)

print(response.choices[0].message.content)
