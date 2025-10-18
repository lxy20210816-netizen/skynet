#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出持仓明细到Markdown格式
"""

import sys
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDENTIALS_FILE = os.path.expanduser('~/Desktop/workspace/skynet/config/credentials.json')
SHEET_ID = '1b55-D54NLbBo1yJd-OjDy7rqCBEkK8Dza3vDLZCPaiU'
WORKSHEET_INDEX = 2  # 资产明细


def read_holdings():
    """读取持仓数据"""
    try:
        print("🔐 正在连接Google Sheets...", file=sys.stderr)
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open_by_key(SHEET_ID)
        worksheet = spreadsheet.get_worksheet(WORKSHEET_INDEX)
        
        print(f"📖 读取工作表: {worksheet.title}", file=sys.stderr)
        
        all_values = worksheet.get_all_values()
        
        if not all_values:
            print("❌ 工作表为空", file=sys.stderr)
            return None
        
        print(f"✅ 成功读取 {len(all_values)} 行数据", file=sys.stderr)
        return all_values
        
    except Exception as e:
        print(f"❌ 读取失败: {e}", file=sys.stderr)
        return None


def format_to_markdown(data):
    """将数据格式化为Markdown"""
    if not data:
        return ""
    
    lines = [
        "# 💼 我的持仓明细\n",
        f"📅 更新时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n",
        "---\n",
    ]
    
    # 提取表头
    headers = data[0]
    
    # 保留所有列，为空表头生成默认名称
    header_indices = []
    clean_headers = []
    for i, h in enumerate(headers):
        header_indices.append(i)
        # 如果表头为空，生成默认列名
        if h.strip():
            clean_headers.append(h)
        else:
            # 将数字索引转换为字母（0->A, 1->B, etc.）
            col_letter = chr(65 + i) if i < 26 else f"列{i+1}"
            clean_headers.append(f"列{col_letter}")
    
    # 输出表格
    if header_indices:
        lines.append("\n## 📊 资产明细\n")
        lines.append("| " + " | ".join(clean_headers) + " |")
        lines.append("|" + "------|" * len(clean_headers))
        
        # 输出数据行
        for row in data[1:]:
            if not any(row):  # 跳过空行
                continue
            
            row_values = []
            for idx in header_indices:
                value = row[idx] if idx < len(row) else ""
                row_values.append(value)
            
            # 只输出非完全空的行
            if any(v.strip() for v in row_values):
                lines.append("| " + " | ".join(row_values) + " |")
        
        lines.append("")
    
    # 添加统计信息
    lines.append("\n## 📈 数据统计\n")
    lines.append(f"- 总行数：{len(data) - 1}行")
    lines.append(f"- 列数：{len(clean_headers)}列")
    lines.append(f"- 数据来源：Google Sheets")
    lines.append(f"- 表格链接：https://docs.google.com/spreadsheets/d/{SHEET_ID}\n")
    
    return '\n'.join(lines)


def main():
    # 读取数据
    data = read_holdings()
    
    if not data:
        sys.exit(1)
    
    # 转换为Markdown
    markdown = format_to_markdown(data)
    
    # 输出到stdout
    print(markdown)
    
    print("\n✅ Markdown数据已生成", file=sys.stderr)


if __name__ == '__main__':
    main()

