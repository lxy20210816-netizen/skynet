#!/usr/bin/env python3
"""
从Google Sheets导出房产数据到本地文件
支持多种格式：JSON、CSV、Excel
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime
import pandas as pd

# Google Sheets相关导入
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    print("错误: 缺少必要的库，请运行: pip install gspread google-auth pandas openpyxl", file=sys.stderr)
    sys.exit(1)

def get_credentials(credentials_file):
    """获取Google Sheets认证"""
    try:
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"认证失败: {e}", file=sys.stderr)
        return None

def export_from_gsheets(sheet_id, worksheet_name, output_dir, credentials_file, formats=['json', 'csv', 'excel']):
    """
    从Google Sheets导出数据到本地文件
    
    参数:
        sheet_id: Google Sheets的ID
        worksheet_name: 工作表名称
        output_dir: 输出目录
        credentials_file: Google服务账号凭证文件路径
        formats: 导出格式列表 ['json', 'csv', 'excel']
    """
    
    if not GSHEETS_AVAILABLE:
        print("❌ 无法连接Google Sheets: 缺少必要的库", file=sys.stderr)
        return False
    
    try:
        print(f"正在连接Google Sheets...")
        print(f"表格ID: {sheet_id}")
        print(f"工作表: {worksheet_name}")
        
        # 认证Google Sheets API
        client = get_credentials(credentials_file)
        if not client:
            return False
        
        # 打开表格
        print(f"正在打开表格...")
        spreadsheet = client.open_by_key(sheet_id)
        print(f"表格名称: {spreadsheet.title}")
        
        # 获取工作表
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            print(f"找到工作表: {worksheet_name}")
        except:
            print(f"❌ 找不到工作表: {worksheet_name}", file=sys.stderr)
            return False
        
        # 获取所有数据
        print(f"正在读取数据...")
        all_data = worksheet.get_all_values()
        
        if not all_data:
            print(f"⚠️  工作表为空", file=sys.stderr)
            return False
        
        # 分离表头和数据
        headers = all_data[0]
        data_rows = all_data[1:]
        
        print(f"📊 数据统计:")
        print(f"   表头列数: {len(headers)}")
        print(f"   数据行数: {len(data_rows)}")
        print(f"   总记录数: {len(data_rows)}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 导出JSON格式
        if 'json' in formats:
            json_file = os.path.join(output_dir, f"real_estate_data_{timestamp}.json")
            export_to_json(headers, data_rows, json_file)
            print(f"✅ JSON文件已保存: {json_file}")
        
        # 导出CSV格式
        if 'csv' in formats:
            csv_file = os.path.join(output_dir, f"real_estate_data_{timestamp}.csv")
            export_to_csv(headers, data_rows, csv_file)
            print(f"✅ CSV文件已保存: {csv_file}")
        
        # 导出Excel格式
        if 'excel' in formats:
            excel_file = os.path.join(output_dir, f"real_estate_data_{timestamp}.xlsx")
            export_to_excel(headers, data_rows, excel_file)
            print(f"✅ Excel文件已保存: {excel_file}")
        
        # 创建数据摘要
        summary_file = os.path.join(output_dir, f"data_summary_{timestamp}.txt")
        create_summary(headers, data_rows, summary_file)
        print(f"✅ 数据摘要已保存: {summary_file}")
        
        print(f"\n🎉 导出完成！")
        print(f"📁 输出目录: {output_dir}")
        print(f"📊 总记录数: {len(data_rows)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导出失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

def export_to_json(headers, data_rows, output_file):
    """导出为JSON格式"""
    data = []
    for row in data_rows:
        record = {}
        for i, header in enumerate(headers):
            if i < len(row):
                record[header] = row[i]
            else:
                record[header] = ""
        data.append(record)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(data),
                "columns": headers
            },
            "data": data
        }, f, ensure_ascii=False, indent=2)

def export_to_csv(headers, data_rows, output_file):
    """导出为CSV格式"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_rows)

def export_to_excel(headers, data_rows, output_file):
    """导出为Excel格式"""
    # 创建DataFrame
    df = pd.DataFrame(data_rows, columns=headers)
    
    # 写入Excel文件
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='房地产数据', index=False)
        
        # 获取工作表对象进行格式化
        worksheet = writer.sheets['房地产数据']
        
        # 设置列宽
        for i, header in enumerate(headers):
            column_letter = chr(65 + i)  # A, B, C, ...
            max_length = max(len(str(header)), 15)
            worksheet.column_dimensions[column_letter].width = min(max_length, 50)

def create_summary(headers, data_rows, output_file):
    """创建数据摘要"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("房地产数据摘要\n")
        f.write("=" * 50 + "\n")
        f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总记录数: {len(data_rows)}\n")
        f.write(f"列数: {len(headers)}\n\n")
        
        f.write("列信息:\n")
        f.write("-" * 30 + "\n")
        for i, header in enumerate(headers):
            f.write(f"{i+1:2d}. {header}\n")
        
        # 统计各地区数据
        if len(headers) > 0 and len(data_rows) > 0:
            area_col_idx = 0  # 假设第一列是地区
            if area_col_idx < len(headers):
                area_counts = {}
                for row in data_rows:
                    if len(row) > area_col_idx:
                        area = row[area_col_idx]
                        area_counts[area] = area_counts.get(area, 0) + 1
                
                f.write(f"\n地区分布:\n")
                f.write("-" * 30 + "\n")
                for area, count in sorted(area_counts.items()):
                    f.write(f"{area}: {count} 条记录\n")
        
        # 统计各类型数据
        if len(headers) > 1 and len(data_rows) > 0:
            type_col_idx = 1  # 假设第二列是类型
            if type_col_idx < len(headers):
                type_counts = {}
                for row in data_rows:
                    if len(row) > type_col_idx:
                        prop_type = row[type_col_idx]
                        type_counts[prop_type] = type_counts.get(prop_type, 0) + 1
                
                f.write(f"\n类型分布:\n")
                f.write("-" * 30 + "\n")
                for prop_type, count in sorted(type_counts.items()):
                    f.write(f"{prop_type}: {count} 条记录\n")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='从Google Sheets导出房产数据到本地文件')
    parser.add_argument('--sheet-id', default='1b55-D54NLbBo1yJd-OjDy7rqCBEkK8Dza3vDLZCPaiU',
                       help='Google Sheets ID（默认：预设表格）')
    parser.add_argument('--worksheet', default='房地产池',
                       help='工作表名称（默认：房地产池）')
    parser.add_argument('--output-dir', default='/Users/a0000/Desktop/workspace/brain/skynet',
                       help='输出目录（默认：/Users/a0000/Desktop/workspace/brain/skynet）')
    parser.add_argument('--credentials', default=os.path.expanduser('~/Desktop/workspace/skynet/config/credentials.json'),
                       help='Google API凭证文件路径')
    parser.add_argument('--formats', nargs='+', default=['json', 'csv', 'excel'],
                       choices=['json', 'csv', 'excel'],
                       help='导出格式（默认：json csv excel）')
    
    args = parser.parse_args()
    
    print("🏠 房地产数据导出工具")
    print("=" * 50)
    print(f"目标表格: {args.sheet_id}")
    print(f"工作表: {args.worksheet}")
    print(f"输出目录: {args.output_dir}")
    print(f"导出格式: {', '.join(args.formats)}")
    print()
    
    # 检查凭证文件
    if not os.path.exists(args.credentials):
        print(f"❌ 找不到凭证文件: {args.credentials}", file=sys.stderr)
        print("请确保Google API凭证文件存在", file=sys.stderr)
        return 1
    
    # 执行导出
    success = export_from_gsheets(
        sheet_id=args.sheet_id,
        worksheet_name=args.worksheet,
        output_dir=args.output_dir,
        credentials_file=args.credentials,
        formats=args.formats
    )
    
    if success:
        print("\n✅ 导出成功完成！")
        return 0
    else:
        print("\n❌ 导出失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
