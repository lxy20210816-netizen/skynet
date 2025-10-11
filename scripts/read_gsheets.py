#!/usr/bin/env python3
"""
从Google Sheets读取数据
支持通过共享链接或表格ID读取数据
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import sys
import argparse

# Google Sheets API范围
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def read_google_sheet(sheet_id_or_url, credentials_file='config/credentials.json', worksheet_index=0):
    """
    从Google Sheets读取数据
    
    参数:
        sheet_id_or_url: Google Sheets的ID或完整URL
        credentials_file: Google服务账号凭证文件路径
        worksheet_index: 工作表索引（0表示第一个工作表）
    
    返回:
        字典格式的数据
    """
    try:
        print(f"正在连接Google Sheets...", file=sys.stderr)
        
        # 认证
        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # 提取Sheet ID（如果传入的是完整URL）
        sheet_id = sheet_id_or_url
        if 'docs.google.com' in sheet_id_or_url or 'spreadsheets' in sheet_id_or_url:
            # 从URL中提取ID
            # URL格式: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit...
            import re
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_id_or_url)
            if match:
                sheet_id = match.group(1)
                print(f"从URL提取Sheet ID: {sheet_id}", file=sys.stderr)
        
        # 打开表格
        print(f"打开表格: {sheet_id}", file=sys.stderr)
        spreadsheet = client.open_by_key(sheet_id)
        
        # 获取工作表信息
        print(f"表格名称: {spreadsheet.title}", file=sys.stderr)
        print(f"工作表数量: {len(spreadsheet.worksheets())}", file=sys.stderr)
        
        # 获取指定工作表
        worksheet = spreadsheet.get_worksheet(worksheet_index)
        print(f"读取工作表: {worksheet.title}", file=sys.stderr)
        
        # 获取所有数据
        all_values = worksheet.get_all_values()
        
        if not all_values:
            print(f"警告: 工作表为空", file=sys.stderr)
            return {
                "success": True,
                "data": {
                    "spreadsheet_title": spreadsheet.title,
                    "worksheet_title": worksheet.title,
                    "rows": 0,
                    "headers": [],
                    "records": []
                }
            }
        
        # 第一行作为表头
        headers = all_values[0]
        print(f"表头: {headers}", file=sys.stderr)
        
        # 转换为字典列表
        records = []
        for row in all_values[1:]:
            if any(row):  # 跳过空行
                record = {}
                for i, header in enumerate(headers):
                    value = row[i] if i < len(row) else ""
                    record[header] = value
                records.append(record)
        
        print(f"成功读取 {len(records)} 行数据", file=sys.stderr)
        
        return {
            "success": True,
            "data": {
                "spreadsheet_title": spreadsheet.title,
                "spreadsheet_url": spreadsheet.url,
                "worksheet_title": worksheet.title,
                "rows": len(records),
                "columns": len(headers),
                "headers": headers,
                "records": records
            }
        }
        
    except FileNotFoundError:
        error_msg = f"找不到凭证文件: {credentials_file}"
        print(f"❌ {error_msg}", file=sys.stderr)
        print(f"\n如何获取credentials.json:", file=sys.stderr)
        print(f"1. 访问 https://console.cloud.google.com/", file=sys.stderr)
        print(f"2. 创建项目并启用Google Sheets API", file=sys.stderr)
        print(f"3. 创建服务账号并下载JSON密钥", file=sys.stderr)
        print(f"4. 将密钥文件保存为 credentials.json", file=sys.stderr)
        print(f"5. 在Google Sheets中与服务账号邮箱共享表格（查看权限）", file=sys.stderr)
        return {"success": False, "error": error_msg}
    
    except gspread.exceptions.SpreadsheetNotFound:
        error_msg = "找不到表格，请检查：1) Sheet ID是否正确 2) 是否已与服务账号共享"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {"success": False, "error": error_msg}
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 读取失败: {error_msg}", file=sys.stderr)
        return {"success": False, "error": error_msg}

def read_specific_range(sheet_id_or_url, range_name, credentials_file='config/credentials.json'):
    """
    读取指定范围的数据
    
    参数:
        sheet_id_or_url: Google Sheets的ID或URL
        range_name: 范围，例如 'Sheet1!A1:D10' 或 'A1:D10'
        credentials_file: 凭证文件路径
    """
    try:
        # 认证
        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # 提取Sheet ID
        sheet_id = sheet_id_or_url
        if '/d/' in sheet_id_or_url:
            import re
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_id_or_url)
            if match:
                sheet_id = match.group(1)
        
        # 打开表格
        spreadsheet = client.open_by_key(sheet_id)
        
        # 获取指定范围的数据
        worksheet = spreadsheet.sheet1  # 默认第一个工作表
        values = worksheet.get(range_name)
        
        print(f"成功读取范围 {range_name}: {len(values)} 行", file=sys.stderr)
        
        return {
            "success": True,
            "data": {
                "range": range_name,
                "values": values
            }
        }
        
    except Exception as e:
        print(f"❌ 读取范围失败: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='从Google Sheets读取数据')
    parser.add_argument('sheet', help='Google Sheets的ID或URL')
    parser.add_argument('-c', '--credentials', default='config/credentials.json', 
                       help='Google API凭证文件路径（默认: credentials.json）')
    parser.add_argument('-w', '--worksheet', type=int, default=0,
                       help='工作表索引（默认: 0，即第一个工作表）')
    parser.add_argument('-r', '--range', help='读取指定范围，例如: A1:D10')
    parser.add_argument('-o', '--output', help='输出文件路径（可选，默认输出到stdout）')
    
    args = parser.parse_args()
    
    print("=" * 60, file=sys.stderr)
    print("Google Sheets 数据读取工具", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # 读取数据
    if args.range:
        result = read_specific_range(args.sheet, args.range, args.credentials)
    else:
        result = read_google_sheet(args.sheet, args.credentials, args.worksheet)
    
    # 输出结果
    json_output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"\n✅ 结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(json_output)
    
    # 显示摘要
    if result.get("success"):
        print(f"\n✅ 读取成功！", file=sys.stderr)
        if result['data'].get('rows'):
            print(f"📊 数据行数: {result['data']['rows']}", file=sys.stderr)
            print(f"📋 列数: {result['data']['columns']}", file=sys.stderr)
            
            # 显示前3条记录示例
            if result['data'].get('records'):
                print(f"\n前3条记录示例:", file=sys.stderr)
                for i, record in enumerate(result['data']['records'][:3], 1):
                    print(f"{i}. {record}", file=sys.stderr)
    else:
        print(f"\n❌ 读取失败: {result.get('error')}", file=sys.stderr)

if __name__ == "__main__":
    main()

