#!/usr/bin/env python3
"""
将Suumo数据上传到Google Sheets
需要先设置Google Sheets API认证
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import sys
import re
from datetime import datetime

# Google Sheets API范围
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def extract_number(text):
    """从文本中提取数字"""
    match = re.search(r'(\d+\.?\d*)', str(text))
    return float(match.group(1)) if match else 0

def upload_to_google_sheets(json_file, credentials_file='config/credentials.json', sheet_name='锦糸町房源'):
    """
    上传数据到Google Sheets
    
    参数:
        json_file: JSON数据文件路径
        credentials_file: Google服务账号凭证文件
        sheet_name: Google Sheets名称
    """
    try:
        # 读取JSON数据
        print(f"读取数据文件: {json_file}", file=sys.stderr)
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data.get('success'):
            print("❌ JSON数据无效", file=sys.stderr)
            return False
        
        properties = data['data']['properties']
        print(f"找到 {len(properties)} 个房源", file=sys.stderr)
        
        # 认证Google Sheets
        print(f"认证Google Sheets API...", file=sys.stderr)
        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # 创建或打开表格
        try:
            spreadsheet = client.open(sheet_name)
            print(f"打开已存在的表格: {sheet_name}", file=sys.stderr)
        except:
            spreadsheet = client.create(sheet_name)
            print(f"创建新表格: {sheet_name}", file=sys.stderr)
        
        worksheet = spreadsheet.sheet1
        
        # 准备表头
        headers = [
            '序号', '物件名称', '价格(万円)', '单价(円/m²)', 
            '面积', '面积(m²)', '户型', '建造年份', '房龄(年)',
            '地址', '链接', '更新时间'
        ]
        
        # 准备数据行
        rows = [headers]
        for idx, prop in enumerate(properties, 1):
            # 提取价格
            price_match = re.search(r'(\d+)万円', prop.get('price', '0'))
            price = int(price_match.group(1)) if price_match else 0
            
            # 提取面积
            area = extract_number(prop.get('area', '0'))
            
            # 提取年份
            year_match = re.search(r'(19|20)(\d{2})', prop.get('age', ''))
            year = int(year_match.group(0)) if year_match else 0
            age_years = 2025 - year if year > 0 else 0
            
            # 计算单价
            price_per_sqm = int((price * 10000 / area)) if area > 0 else 0
            
            row = [
                idx,
                prop.get('building_name', 'N/A'),
                price,
                price_per_sqm,
                prop.get('area', 'N/A'),
                f"{area:.2f}" if area > 0 else 'N/A',
                prop.get('layout', 'N/A'),
                year if year > 0 else 'N/A',
                age_years if age_years > 0 else 'N/A',
                prop.get('address', 'N/A'),
                prop.get('url', 'N/A'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            rows.append(row)
        
        # 清空并更新表格
        print(f"正在更新表格数据...", file=sys.stderr)
        worksheet.clear()
        worksheet.update(rows, value_input_option='USER_ENTERED')
        
        # 格式化表格
        print(f"格式化表格...", file=sys.stderr)
        
        # 冻结首行
        worksheet.freeze(rows=1)
        
        # 设置列宽
        worksheet.format('A1:L1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
        })
        
        # 设置价格列格式
        worksheet.format('C2:C100', {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}})
        worksheet.format('D2:D100', {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}})
        
        print(f"\n✅ 上传成功！", file=sys.stderr)
        print(f"📊 表格链接: {spreadsheet.url}", file=sys.stderr)
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: 找不到文件", file=sys.stderr)
        print(f"   请确保以下文件存在:", file=sys.stderr)
        print(f"   1. {json_file} - 数据文件", file=sys.stderr)
        print(f"   2. {credentials_file} - Google API凭证文件", file=sys.stderr)
        print(f"\n如何获取credentials.json:", file=sys.stderr)
        print(f"   1. 访问 https://console.cloud.google.com/", file=sys.stderr)
        print(f"   2. 创建项目并启用Google Sheets API", file=sys.stderr)
        print(f"   3. 创建服务账号并下载JSON密钥", file=sys.stderr)
        print(f"   4. 将密钥文件重命名为credentials.json", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ 上传失败: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    main()

