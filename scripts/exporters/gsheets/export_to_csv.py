#!/usr/bin/env python3
"""
将Suumo抓取的JSON数据导出为CSV格式
方便导入到Google Sheets
"""

import json
import csv
import sys
import re
from datetime import datetime

def extract_number(text):
    """从文本中提取数字"""
    match = re.search(r'(\d+\.?\d*)', str(text))
    return float(match.group(1)) if match else 0

def json_to_csv(json_file, csv_file):
    """将JSON数据转换为CSV"""
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data.get('success'):
            print(f"❌ JSON数据获取失败", file=sys.stderr)
            return False
        
        properties = data['data']['properties']
        print(f"正在转换 {len(properties)} 个房源数据...", file=sys.stderr)
        
        # 准备CSV数据
        rows = []
        for idx, prop in enumerate(properties, 1):
            # 提取价格数字
            price_match = re.search(r'(\d+)万円', prop.get('price', '0'))
            price = int(price_match.group(1)) if price_match else 0
            
            # 提取面积数字
            area = extract_number(prop.get('area', '0'))
            
            # 提取建造年份
            year_match = re.search(r'(19|20)(\d{2})', prop.get('age', ''))
            year = int(year_match.group(0)) if year_match else 0
            age_years = 2025 - year if year > 0 else 0
            
            # 计算单价
            price_per_sqm = int((price * 10000 / area)) if area > 0 else 0
            
            row = {
                '序号': idx,
                '物件名称': prop.get('building_name', 'N/A'),
                '价格(万円)': price,
                '单价(円/m²)': price_per_sqm,
                '面积': prop.get('area', 'N/A'),
                '面积(m²)': f"{area:.2f}" if area > 0 else 'N/A',
                '户型': prop.get('layout', 'N/A'),
                '建造年份': year if year > 0 else 'N/A',
                '房龄(年)': age_years if age_years > 0 else 'N/A',
                '地址': prop.get('address', 'N/A'),
                '链接': prop.get('url', 'N/A'),
            }
            rows.append(row)
        
        # 写入CSV文件
        if rows:
            fieldnames = ['序号', '物件名称', '价格(万円)', '单价(円/m²)', '面积', '面积(m²)', 
                         '户型', '建造年份', '房龄(年)', '地址', '链接']
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:  # utf-8-sig for Excel
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"✅ CSV文件已生成: {csv_file}", file=sys.stderr)
            print(f"📊 包含 {len(rows)} 条记录", file=sys.stderr)
            print(f"\n使用方法:", file=sys.stderr)
            print(f"  1. 打开 Google Sheets", file=sys.stderr)
            print(f"  2. 文件 -> 导入 -> 上传", file=sys.stderr)
            print(f"  3. 选择 {csv_file}", file=sys.stderr)
            print(f"  4. 导入位置选择：替换当前工作表", file=sys.stderr)
            
            return True
        else:
            print(f"❌ 没有数据可以导出", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 转换失败: {e}", file=sys.stderr)
        return False

def main():
    """主函数"""
    json_file = 'kinshicho_sale_final.json'
    csv_file = 'kinshicho_sale.csv'
    
    print("=" * 60, file=sys.stderr)
    print("Suumo数据导出为CSV（可导入Google Sheets）", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    success = json_to_csv(json_file, csv_file)
    
    if success:
        print(f"\n🎉 导出成功！", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"\n❌ 导出失败！", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

