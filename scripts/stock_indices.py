#!/usr/bin/env python3
"""
股票指数数据获取脚本
使用yfinance获取纳斯达克、纳斯达克100、日经225、VIX指数的最新收盘价
数据保存到MySQL数据库的stock_indices表中
"""

import yfinance as yf
import datetime
import json
import sys
import pymysql
from decimal import Decimal

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

def get_stock_indices():
    """获取股票指数数据 - 获取前一个交易日的收盘价"""
    try:
        print("开始获取股票指数数据（前一个交易日）...", file=sys.stderr)
        
        # 定义要获取的指数代码
        indices = {
            'nasdaq': '^IXIC',      # 纳斯达克综合指数
            'nasdaq_100': '^NDX',   # 纳斯达克100指数
            'n225': '^N225',        # 日经225指数
            'vix': '^VIX'           # VIX恐慌指数
        }
        
        results = {}
        trading_date = None
        
        for name, symbol in indices.items():
            try:
                print(f"正在获取 {name} ({symbol}) 数据...", file=sys.stderr)
                
                # 获取股票数据
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="10d")  # 获取最近10天数据，确保有前一个交易日
                
                if hist.empty:
                    print(f"警告: {name} 没有获取到数据", file=sys.stderr)
                    results[name] = 0.0
                    continue
                
                # 显示最近几天的数据用于调试
                print(f"{name} 最近几天数据:", file=sys.stderr)
                for i, (date, row) in enumerate(hist.tail(5).iterrows()):
                    print(f"  {i}: {date.date()} - 收盘价: {row['Close']:.3f}", file=sys.stderr)
                
                # 获取最新的交易日收盘价（最后一个数据点）
                if len(hist) >= 1:
                    latest_close = hist['Close'].iloc[-1]  # 最新交易日收盘价
                    latest_date = hist.index[-1].date()    # 最新交易日日期
                    results[name] = float(latest_close)
                    
                    # 记录交易日期（所有指数应该使用相同的日期）
                    if trading_date is None:
                        trading_date = latest_date
                    
                    print(f"{name} 最新交易日({latest_date})收盘价: {latest_close:.3f}", file=sys.stderr)
                else:
                    print(f"警告: {name} 数据不足，无法获取最新交易日数据", file=sys.stderr)
                    results[name] = 0.0
                
            except Exception as e:
                print(f"获取 {name} 数据时出错: {e}", file=sys.stderr)
                results[name] = 0.0
        
        # 如果没有获取到任何交易日期，使用昨天作为默认日期
        if trading_date is None:
            trading_date = datetime.date.today() - datetime.timedelta(days=1)
            print(f"未获取到交易日期，使用默认日期: {trading_date}", file=sys.stderr)
        
        # 返回结果
        return {
            "success": True,
            "data": {
                "date": trading_date.strftime("%Y-%m-%d"),
                "nasdaq": results.get('nasdaq', 0.0),
                "nasdaq_100": results.get('nasdaq_100', 0.0),
                "n225": results.get('n225', 0.0),
                "vix": results.get('vix', 0.0),
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"获取股票指数数据时出错: {e}", file=sys.stderr)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }

def save_to_database(data):
    """将股票指数数据保存到数据库"""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        with connection.cursor() as cursor:
            # 检查该日期是否已存在数据
            check_sql = "SELECT id FROM stock_indices WHERE date = %s"
            cursor.execute(check_sql, (data['date'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                update_sql = """
                UPDATE stock_indices 
                SET nasdaq = %s, nasdaq_100 = %s, n225 = %s, vix = %s
                WHERE date = %s
                """
                cursor.execute(update_sql, (
                    data['nasdaq'], 
                    data['nasdaq_100'], 
                    data['n225'], 
                    data['vix'],
                    data['date']
                ))
                print(f"更新数据库记录: 日期 {data['date']}", file=sys.stderr)
            else:
                # 插入新记录
                insert_sql = """
                INSERT INTO stock_indices (date, nasdaq, nasdaq_100, nasdaq_100_pe, n225, vix, a)
                VALUES (%s, %s, %s, 0, %s, %s, 0)
                """
                cursor.execute(insert_sql, (
                    data['date'],
                    data['nasdaq'], 
                    data['nasdaq_100'], 
                    data['n225'], 
                    data['vix']
                ))
                print(f"插入新数据库记录: 日期 {data['date']}", file=sys.stderr)
            
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

def main():
    """主函数"""
    try:
        print("开始执行股票指数数据获取...", file=sys.stderr)
        
        # 获取股票指数数据
        result = get_stock_indices()
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            print(f"获取到数据: {data}", file=sys.stderr)
            
            # 保存到数据库
            print("准备保存到数据库...", file=sys.stderr)
            db_success = save_to_database(data)
            
            if db_success:
                result["database_saved"] = True
                print("数据已成功保存到数据库", file=sys.stderr)
            else:
                result["database_saved"] = False
                result["database_error"] = "数据库保存失败"
                print("数据库保存失败", file=sys.stderr)
        
        # 输出JSON格式结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"主函数执行出错: {e}", file=sys.stderr)
        error_result = {
            "success": False,
            "error": f"脚本执行错误: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
