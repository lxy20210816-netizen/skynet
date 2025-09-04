import requests
import re
import json

url = "https://www.macrotrends.net/stocks/charts/NDAQ/nasdaq/pe-ratio"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)
html = resp.text

# 找到隐藏在脚本里的数据
m = re.search(r'var historical_data = (\[.*?\]);', html, re.S)
if m:
    data = json.loads(m.group(1))
    # 打印最近两天的 PE
    for row in data[:2]:
        print(row['date'], row['value'])
else:
    print("没找到历史数据")
