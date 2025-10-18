#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出房地产池数据到Markdown格式
从Google Sheets读取数据，美化输出到指定目录
"""

import os
import sys
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from collections import defaultdict

# Google Sheets API配置
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = os.path.expanduser('~/Desktop/workspace/skynet/config/credentials.json')
SHEET_ID = '1b55-D54NLbBo1yJd-OjDy7rqCBEkK8Dza3vDLZCPaiU'
WORKSHEET_NAME = '房地产池'

# 输出目录
OUTPUT_DIR = os.path.expanduser('~/Desktop/workspace/brain/不动产池')


def read_from_google_sheets():
    """从Google Sheets读取数据"""
    try:
        print("🔐 正在认证Google Sheets...", file=sys.stderr)
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        print(f"📖 正在打开表格...", file=sys.stderr)
        spreadsheet = client.open_by_key(SHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        print(f"📥 正在读取数据...", file=sys.stderr)
        all_values = worksheet.get_all_values()
        
        if not all_values:
            print("❌ 工作表为空", file=sys.stderr)
            return []
        
        headers = all_values[0]
        data = []
        
        for row in all_values[1:]:
            if not any(row):  # 跳过空行
                continue
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_dict[header] = row[i]
                else:
                    row_dict[header] = ''
            data.append(row_dict)
        
        print(f"✅ 成功读取 {len(data)} 条数据", file=sys.stderr)
        return data
    
    except FileNotFoundError:
        print(f"❌ 找不到凭证文件: {CREDENTIALS_FILE}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 读取数据失败: {e}", file=sys.stderr)
        sys.exit(1)


def parse_price(price_str):
    """解析价格字符串，返回数值"""
    if not price_str:
        return 0
    try:
        # 移除逗号，只保留数字
        price_str = price_str.replace(',', '').strip()
        return float(price_str) if price_str else 0
    except:
        return 0


def parse_area(area_str):
    """解析面积字符串，返回数值"""
    if not area_str:
        return 0
    try:
        # 提取第一个数字
        import re
        match = re.search(r'([\d.]+)', area_str)
        return float(match.group(1)) if match else 0
    except:
        return 0


def format_property(prop):
    """格式化单个房产信息为Markdown"""
    lines = []
    
    # 标题
    building_name = prop.get('🏢 物件名称', 'N/A')
    lines.append(f"### {building_name}\n")
    
    # 基本信息表格
    lines.append("| 项目 | 信息 |")
    lines.append("|------|------|")
    
    # 价格
    price = prop.get('💰 价格(万円)', '')
    price_per_sqm = prop.get('📊 单价(万円/m²)', '')
    if price:
        lines.append(f"| 💰 价格 | **{price}万円** |")
    if price_per_sqm:
        lines.append(f"| 📊 单价 | {price_per_sqm} 万円/m² |")
    
    # 面积和户型
    area = prop.get('📏 面积(m²)', '')
    layout = prop.get('🏠 户型', '')
    if area:
        lines.append(f"| 📏 面积 | {area}m² |")
    if layout:
        lines.append(f"| 🏠 户型 | {layout} |")
    
    # 建筑年份和房龄
    year = prop.get('📅 建造年份', '')
    age = prop.get('⏳ 房龄(年)', '')
    if year:
        lines.append(f"| 📅 建造年份 | {year}年 |")
    if age:
        lines.append(f"| ⏳ 房龄 | {age}年 |")
    
    # 地址
    address = prop.get('📍 地址', '')
    if address:
        lines.append(f"| 📍 地址 | {address} |")
    
    # 交通
    access = prop.get('🚇 交通', '')
    if access and access != 'N/A':
        lines.append(f"| 🚇 交通 | {access} |")
    
    # 链接
    url = prop.get('🔗 详情链接', '')
    if url and url != 'N/A':
        lines.append(f"| 🔗 详情 | [查看详情]({url}) |")
    
    lines.append("")  # 空行
    return '\n'.join(lines)


def generate_markdown(data):
    """生成Markdown文档"""
    # 按地区和类型分组
    grouped = defaultdict(lambda: defaultdict(list))
    
    for prop in data:
        region = prop.get('🗺️ 地区', '未知')
        prop_type = prop.get('🏘️ 类型', '未知')
        grouped[region][prop_type].append(prop)
    
    # 生成总览文档
    overview_lines = [
        "# 🏘️ 不动产池子总览\n",
        f"📅 更新时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n",
        "---\n",
    ]
    
    # 统计信息
    total_count = len(data)
    overview_lines.append(f"📊 **总房源数量**: {total_count} 个\n")
    
    # 按地区统计
    overview_lines.append("## 📍 地区分布\n")
    for region in sorted(grouped.keys()):
        region_count = sum(len(props) for props in grouped[region].values())
        overview_lines.append(f"- **{region}**: {region_count} 个房源")
        for prop_type in sorted(grouped[region].keys()):
            count = len(grouped[region][prop_type])
            overview_lines.append(f"  - {prop_type}: {count} 个")
    overview_lines.append("")
    
    # 价格分析
    overview_lines.append("## 💰 价格分析\n")
    
    prices = []
    for prop in data:
        price = parse_price(prop.get('💰 价格(万円)', ''))
        if price > 0:
            prices.append(price)
    
    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        overview_lines.append(f"- 平均价格: **{avg_price:.0f}万円**")
        overview_lines.append(f"- 最低价格: {min_price:.0f}万円")
        overview_lines.append(f"- 最高价格: {max_price:.0f}万円")
        overview_lines.append("")
    
    # 面积分析
    overview_lines.append("## 📏 面积分析\n")
    
    areas = []
    for prop in data:
        area = parse_area(prop.get('📏 面积(m²)', ''))
        if area > 0:
            areas.append(area)
    
    if areas:
        avg_area = sum(areas) / len(areas)
        min_area = min(areas)
        max_area = max(areas)
        
        overview_lines.append(f"- 平均面积: **{avg_area:.2f}m²**")
        overview_lines.append(f"- 最小面积: {min_area:.2f}m²")
        overview_lines.append(f"- 最大面积: {max_area:.2f}m²")
        overview_lines.append("")
    
    # 地区链接导航
    overview_lines.append("## 🗂️ 分区详情\n")
    for region in sorted(grouped.keys()):
        safe_region = region.replace('/', '_')
        overview_lines.append(f"- [{region}](./{safe_region}/README.md)")
    overview_lines.append("")
    
    return '\n'.join(overview_lines), grouped


def generate_region_markdown(region, properties_by_type):
    """生成地区详情Markdown"""
    lines = [
        f"# 🗺️ {region}\n",
        f"📅 更新时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n",
        "---\n",
    ]
    
    # 统计信息
    total = sum(len(props) for props in properties_by_type.values())
    lines.append(f"📊 **房源数量**: {total} 个\n")
    
    # 按类型导航
    lines.append("## 📑 分类\n")
    for prop_type in sorted(properties_by_type.keys()):
        count = len(properties_by_type[prop_type])
        safe_type = prop_type.replace('/', '_')
        lines.append(f"- [{prop_type}](./{safe_type}.md) ({count}个)")
    lines.append("\n---\n")
    
    # 返回首页链接
    lines.append("[← 返回总览](../README.md)\n")
    
    return '\n'.join(lines)


def generate_type_markdown(region, prop_type, properties):
    """生成类型详情Markdown"""
    lines = [
        f"# {region} - {prop_type}\n",
        f"📅 更新时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n",
        f"📊 房源数量：{len(properties)} 个\n",
        "---\n",
    ]
    
    # 按价格排序
    properties_sorted = sorted(properties, key=lambda x: parse_price(x.get('💰 价格(万円)', '')))
    
    # 输出每个房产
    for i, prop in enumerate(properties_sorted, 1):
        lines.append(f"## {i}. {prop.get('🏢 物件名称', 'N/A')}\n")
        lines.append(format_property(prop))
        lines.append("---\n")
    
    # 返回链接
    safe_region = region.replace('/', '_')
    lines.append(f"[← 返回{region}](./{safe_region}/README.md) | [← 返回总览](../README.md)\n")
    
    return '\n'.join(lines)


def generate_unified_markdown(data):
    """生成统一的Markdown文档"""
    # 按地区和类型分组
    grouped = defaultdict(lambda: defaultdict(list))
    
    for prop in data:
        region = prop.get('🗺️ 地区', '未知')
        prop_type = prop.get('🏘️ 类型', '未知')
        grouped[region][prop_type].append(prop)
    
    # 生成文档
    lines = [
        "# 🏘️ 不动产池\n",
        f"📅 更新时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n",
        "---\n",
    ]
    
    # 统计信息
    total_count = len(data)
    lines.append(f"📊 **总房源数量**: {total_count} 个\n")
    
    # 价格统计
    prices = []
    for prop in data:
        price = parse_price(prop.get('💰 价格(万円)', ''))
        if price > 0:
            prices.append(price)
    
    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        lines.append(f"💰 **价格区间**: {min_price:.0f}万円 - {max_price:.0f}万円（平均 {avg_price:.0f}万円）\n")
    
    # 面积统计
    areas = []
    for prop in data:
        area = parse_area(prop.get('📏 面积(m²)', ''))
        if area > 0:
            areas.append(area)
    
    if areas:
        avg_area = sum(areas) / len(areas)
        lines.append(f"📏 **面积区间**: {min(areas):.1f}m² - {max(areas):.1f}m²（平均 {avg_area:.1f}m²）\n")
    
    lines.append("\n---\n")
    
    # 按地区输出
    for region in sorted(grouped.keys()):
        lines.append(f"\n## 📍 {region}\n")
        
        properties_by_type = grouped[region]
        total_region = sum(len(props) for props in properties_by_type.values())
        lines.append(f"**房源数量**: {total_region} 个\n")
        
        # 按类型输出
        for prop_type in sorted(properties_by_type.keys()):
            properties = properties_by_type[prop_type]
            lines.append(f"\n### {prop_type} ({len(properties)}个)\n")
            
            # 按价格排序
            properties_sorted = sorted(properties, key=lambda x: parse_price(x.get('💰 价格(万円)', '')))
            
            # 输出每个房产
            for i, prop in enumerate(properties_sorted, 1):
                building_name = prop.get('🏢 物件名称', 'N/A')
                price = prop.get('💰 价格(万円)', '')
                price_per_sqm = prop.get('📊 单价(万円/m²)', '')
                area = prop.get('📏 面积(m²)', '')
                layout = prop.get('🏠 户型', '')
                year = prop.get('📅 建造年份', '')
                age = prop.get('⏳ 房龄(年)', '')
                address = prop.get('📍 地址', '')
                url = prop.get('🔗 详情链接', '')
                
                # 简洁格式
                lines.append(f"\n**{i}. {building_name}**")
                
                info_parts = []
                if price:
                    info_parts.append(f"💰 {price}万円")
                if price_per_sqm:
                    info_parts.append(f"📊 {price_per_sqm}万円/m²")
                if area:
                    info_parts.append(f"📏 {area}m²")
                if layout:
                    info_parts.append(f"🏠 {layout}")
                if year:
                    info_parts.append(f"📅 {year}年")
                if age:
                    info_parts.append(f"⏳ {age}年")
                
                if info_parts:
                    lines.append(" | " + " | ".join(info_parts))
                
                if address:
                    lines.append(f"  \n📍 {address}")
                
                if url and url != 'N/A':
                    lines.append(f"  \n🔗 [详情]({url})")
                
                lines.append("")  # 空行
            
            lines.append("")  # 类型之间空行
    
    return '\n'.join(lines)


def export_data(data):
    """导出数据到Markdown文件"""
    try:
        # 创建输出目录
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"📁 输出目录: {OUTPUT_DIR}", file=sys.stderr)
        
        # 生成统一的Markdown文档
        full_markdown = generate_unified_markdown(data)
        
        # 写入主文件
        main_path = os.path.join(OUTPUT_DIR, '不动产池.md')
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(full_markdown)
        print(f"✅ 已生成主文档: 不动产池.md", file=sys.stderr)
        
        # 生成JSON备份
        json_path = os.path.join(OUTPUT_DIR, 'data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已生成JSON备份: data.json", file=sys.stderr)
        
        print(f"\n🎉 导出完成！", file=sys.stderr)
        print(f"📂 文件位置: {OUTPUT_DIR}", file=sys.stderr)
        print(f"📄 主文档: 不动产池.md", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ 导出失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    print("=" * 60, file=sys.stderr)
    print("🏘️  不动产池子导出工具", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # 读取数据
    data = read_from_google_sheets()
    
    if not data:
        print("❌ 没有数据可导出", file=sys.stderr)
        sys.exit(1)
    
    # 导出数据
    export_data(data)
    
    print("\n✨ 所有操作完成！", file=sys.stderr)


if __name__ == '__main__':
    main()

