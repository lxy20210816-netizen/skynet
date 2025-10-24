#!/usr/bin/env python3
"""
清理Google Sheets中的重复数据
基于URL、地区、类型、物件名称进行去重
"""

import os
import sys
import argparse
from datetime import datetime

# Google Sheets相关导入
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    print("错误: 缺少必要的库，请运行: pip install gspread google-auth", file=sys.stderr)
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

def clean_duplicates(sheet_id, worksheet_name, credentials_file):
    """
    清理Google Sheets中的重复数据
    
    参数:
        sheet_id: Google Sheets的ID
        worksheet_name: 工作表名称
        credentials_file: Google服务账号凭证文件路径
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
        
        if not all_data or len(all_data) <= 1:
            print(f"⚠️  工作表为空或只有表头", file=sys.stderr)
            return True
        
        headers = all_data[0]
        data_rows = all_data[1:]
        
        print(f"📊 原始数据统计:")
        print(f"   表头列数: {len(headers)}")
        print(f"   数据行数: {len(data_rows)}")
        
        # 去重逻辑
        seen_records = set()
        unique_rows = []
        duplicate_count = 0
        
        for i, row in enumerate(data_rows):
            if len(row) < 13:  # 确保有足够的列
                print(f"⚠️  第{i+2}行数据不完整，跳过")
                continue
            
            # 提取关键字段
            region = row[0] if len(row) > 0 else ""
            prop_type = row[1] if len(row) > 1 else ""
            name = row[3] if len(row) > 3 else ""
            url = row[12] if len(row) > 12 else ""
            
            # 创建唯一标识
            composite_key = f"{region}|{prop_type}|{name}|{url}"
            
            if composite_key in seen_records:
                duplicate_count += 1
                print(f"⏭️  发现重复记录: {name[:30]}... (第{i+2}行)")
            else:
                seen_records.add(composite_key)
                unique_rows.append(row)
        
        print(f"\n📊 去重结果:")
        print(f"   原始记录: {len(data_rows)}")
        print(f"   重复记录: {duplicate_count}")
        print(f"   唯一记录: {len(unique_rows)}")
        
        if duplicate_count == 0:
            print(f"✅ 没有发现重复数据")
            return True
        
        # 询问是否清理
        print(f"\n是否要清理重复数据？")
        print(f"这将删除 {duplicate_count} 条重复记录")
        response = input("输入 'yes' 确认清理: ").strip().lower()
        
        if response != 'yes':
            print(f"❌ 用户取消清理操作")
            return False
        
        # 准备清理后的数据
        cleaned_data = [headers] + unique_rows
        
        # 清空工作表并写入清理后的数据
        print(f"正在清理重复数据...")
        worksheet.clear()
        worksheet.update(values=cleaned_data, range_name='A1', value_input_option='USER_ENTERED')
        
        # 格式化表格
        print(f"正在格式化表格...")
        worksheet.freeze(rows=1)
        
        # 设置表头样式
        worksheet.format('A1:N1', {
            'textFormat': {
                'bold': True,
                'fontSize': 11
            },
            'backgroundColor': {
                'red': 0.2,
                'green': 0.6,
                'blue': 0.86
            },
            'horizontalAlignment': 'CENTER',
            'verticalAlignment': 'MIDDLE'
        })
        
        print(f"\n✅ 清理完成！")
        print(f"📊 最终统计:")
        print(f"   保留记录: {len(unique_rows)}")
        print(f"   删除记录: {duplicate_count}")
        print(f"   清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 清理失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='清理Google Sheets中的重复房产数据')
    parser.add_argument('--sheet-id', default='1b55-D54NLbBo1yJd-OjDy7rqCBEkK8Dza3vDLZCPaiU',
                       help='Google Sheets ID（默认：预设表格）')
    parser.add_argument('--worksheet', default='房地产池',
                       help='工作表名称（默认：房地产池）')
    parser.add_argument('--credentials', default=os.path.expanduser('~/Desktop/workspace/skynet/config/credentials.json'),
                       help='Google API凭证文件路径')
    
    args = parser.parse_args()
    
    print("🧹 Google Sheets重复数据清理工具")
    print("=" * 50)
    print(f"目标表格: {args.sheet_id}")
    print(f"工作表: {args.worksheet}")
    print()
    
    # 检查凭证文件
    if not os.path.exists(args.credentials):
        print(f"❌ 找不到凭证文件: {args.credentials}", file=sys.stderr)
        print("请确保Google API凭证文件存在", file=sys.stderr)
        return 1
    
    # 执行清理
    success = clean_duplicates(
        sheet_id=args.sheet_id,
        worksheet_name=args.worksheet,
        credentials_file=args.credentials
    )
    
    if success:
        print("\n✅ 清理操作完成！")
        return 0
    else:
        print("\n❌ 清理操作失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
