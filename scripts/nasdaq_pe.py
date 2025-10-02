#!/usr/bin/env python3
"""
从GuruFocus获取纳斯达克100 PE比率 - n8n版本
使用Selenium模拟真实浏览器行为，绕过反爬虫机制
适配n8n环境，返回JSON格式数据
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import time
import random
import re
import json
import sys
import os
import pymysql

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='finances',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}", file=sys.stderr)
        return None

def save_to_database(pe_ratio, date_str):
    """将PE比率数据保存到数据库"""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        with connection.cursor() as cursor:
            # 检查该日期是否已存在数据
            check_sql = "SELECT id FROM stock_indices WHERE date = %s"
            cursor.execute(check_sql, (date_str,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                update_sql = """
                UPDATE stock_indices 
                SET nasdaq_100_pe = %s 
                WHERE date = %s
                """
                cursor.execute(update_sql, (pe_ratio, date_str))
                print(f"更新数据库记录: 日期 {date_str}, PE比率 {pe_ratio}", file=sys.stderr)
            else:
                # 插入新记录（其他字段设为0，只更新nasdaq_100_pe）
                insert_sql = """
                INSERT INTO stock_indices (date, nasdaq, nasdaq_100, nasdaq_100_pe, n225, vix, a)
                VALUES (%s, 0, 0, %s, 0, 0, 0)
                """
                cursor.execute(insert_sql, (date_str, pe_ratio))
                print(f"插入新数据库记录: 日期 {date_str}, PE比率 {pe_ratio}", file=sys.stderr)
            
            connection.commit()
            return True
            
    except Exception as e:
        print(f"数据库操作失败: {e}", file=sys.stderr)
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()

def get_nasdaq100_pe():
    """使用Selenium获取纳斯达克100 PE比率 - 获取最新数据"""
    url = "https://www.gurufocus.com/economic_indicators/6778/nasdaq-100-pe-ratio"
    driver = None
    
    try:
        print("正在从GuruFocus获取纳斯达克100 PE数据...", file=sys.stderr)
        
        # 设置Chrome浏览器选项 - 适配n8n环境
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--headless")  # n8n环境通常需要无头模式
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 禁用图片加载以提高速度
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 设置ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 执行反检测脚本
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("浏览器启动成功，正在访问页面...", file=sys.stderr)
        driver.get(url)
        
        # 模拟人类行为
        time.sleep(random.uniform(2, 4))
        
        # 模拟鼠标移动
        driver.execute_script("""
            var event = new MouseEvent('mousemove', {
                'view': window,
                'bubbles': true,
                'cancelable': true,
                'clientX': Math.random() * window.innerWidth,
                'clientY': Math.random() * window.innerHeight
            });
            document.dispatchEvent(event);
        """)
        
        time.sleep(random.uniform(1, 2))
        
        # 检查页面是否正常加载
        if "403" in driver.title or "Forbidden" in driver.page_source:
            print("页面访问被拒绝", file=sys.stderr)
            return None
        
        print("页面加载成功，开始提取数据...", file=sys.stderr)
        
        # 获取页面源码
        page_source = driver.page_source
        
        # 直接查找"Nasdaq 100 PE Ratio was xxx as of 2025-xx-xx"格式的最新数据
        print("查找页面中的'Nasdaq 100 PE Ratio was xxx as of 2025-xx-xx'格式数据...", file=sys.stderr)
        
        # 使用正则表达式匹配这个格式
        nasdaq_pattern = r'Nasdaq 100 PE Ratio was (\d+\.?\d*) as of (\d{4}-\d{2}-\d{2})'
        matches = re.findall(nasdaq_pattern, page_source, re.IGNORECASE)
        
        if matches:
            print(f"找到 {len(matches)} 个匹配的Nasdaq 100 PE Ratio数据:", file=sys.stderr)
            for i, (pe_value, date) in enumerate(matches):
                print(f"  {i+1}. PE比率: {pe_value}, 日期: {date}", file=sys.stderr)
            
            # 选择最新的数据（最后一个）
            latest_pe, latest_date = matches[-1]
            print(f"选择最新数据: PE比率 {latest_pe}, 日期 {latest_date}", file=sys.stderr)
            
            # 返回JSON格式数据
            result = {
                "success": True,
                "data": {
                    "pe_ratio": float(latest_pe),
                    "date": latest_date,
                    "source": "GuruFocus",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "description": f"Nasdaq 100 PE Ratio: {latest_pe} (As of {latest_date})"
                }
            }
            return result
        
        # 如果主要格式没找到，尝试其他格式
        print("主要格式未找到，尝试其他格式...", file=sys.stderr)
        
        # 使用正则表达式提取PE比率
        pe_patterns = [
            r'Nasdaq 100 PE Ratio\s*:?\s*(\d+\.?\d*)',
            r'PE\s*Ratio\s*:?\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*\(.*PE.*\)',
            r'PE.*?(\d+\.?\d*)'
        ]
        
        for i, pattern in enumerate(pe_patterns):
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                pe_value = matches[0]
                print(f"找到PE比率: {pe_value}", file=sys.stderr)
                
                result = {
                    "success": True,
                    "data": {
                        "pe_ratio": float(pe_value),
                        "date": "未知",
                        "source": "GuruFocus",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "description": f"Nasdaq 100 PE Ratio: {pe_value}"
                    }
                }
                return result
        
        # 如果都没找到
        print("未找到PE比率信息", file=sys.stderr)
        return {
            "success": False,
            "error": "未找到PE比率信息",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"获取数据时出错: {e}", file=sys.stderr)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭", file=sys.stderr)

def main():
    """主函数 - 适配n8n"""
    try:
        print("开始执行main函数...", file=sys.stderr)
        result = get_nasdaq100_pe()
        print(f"获取到结果: {result}", file=sys.stderr)
        
        # 如果成功获取数据，保存到数据库
        if result and result.get("success") and result.get("data"):
            pe_ratio = result["data"]["pe_ratio"]
            date_str = result["data"]["date"]
            
            print(f"准备保存到数据库: PE比率 {pe_ratio}, 日期 {date_str}", file=sys.stderr)
            db_success = save_to_database(pe_ratio, date_str)
            
            if db_success:
                result["database_saved"] = True
                print("数据已成功保存到数据库", file=sys.stderr)
            else:
                result["database_saved"] = False
                result["database_error"] = "数据库保存失败"
                print("数据库保存失败", file=sys.stderr)
        
        # 输出JSON格式结果到stdout（n8n会读取这个）
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"main函数出错: {e}", file=sys.stderr)
        error_result = {
            "success": False,
            "error": f"脚本执行错误: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
