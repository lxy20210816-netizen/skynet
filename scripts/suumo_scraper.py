#!/usr/bin/env python3
"""
Suumo房地产信息抓取脚本
使用Selenium抓取Suumo网站的房产信息
支持直接上传到Google Sheets
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import json
import sys
import re
import argparse
from datetime import datetime

# Google Sheets相关导入
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    print("提示: 未安装gspread库，无法上传到Google Sheets", file=sys.stderr)
    print("安装方法: pip install gspread google-auth", file=sys.stderr)

def setup_driver():
    """配置并启动Chrome浏览器"""
    try:
        print("正在启动浏览器...", file=sys.stderr)
        
        # 设置Chrome浏览器选项
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # chrome_options.add_argument("--headless")  # 取消注释可以无头模式运行
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 设置ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 执行反检测脚本
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("浏览器启动成功", file=sys.stderr)
        return driver
        
    except Exception as e:
        print(f"启动浏览器失败: {e}", file=sys.stderr)
        return None

def scrape_suumo_sale(station="錦糸町", area_code="13107", property_type="mansion", max_pages=3):
    """
    抓取Suumo售房信息 - 指定区域的买房信息
    
    参数:
        station: 车站名称（如：錦糸町、亀戸）
        area_code: 区域代码（13107=墨田区, 13108=江东区）
        property_type: 房屋类型（mansion=公寓, house=一户建）
        max_pages: 最大抓取页数
    """
    driver = None
    properties = []
    
    try:
        driver = setup_driver()
        if not driver:
            return {"success": False, "error": "浏览器启动失败"}
        
        # 构建URL
        # 一户建和公寓使用完全不同的URL结构
        
        # 区域代码到URL路径映射
        area_code_to_path = {
            "13107": "sumida",    # 墨田区
            "13108": "koto",      # 江东区
            "13119": "itabashi",  # 板桥区
            "13121": "adachi",    # 足立区
            "13112": "setagaya",  # 世田谷区
        }
        
        area_name_map = {
            "13107": "墨田区",
            "13108": "江东区",
            "13119": "板桥区",
            "13121": "足立区",
            "13112": "世田谷区",
        }
        
        type_name_map = {
            "mansion": "二手公寓",
            "house": "二手一户建"
        }
        
        area_path = area_code_to_path.get(area_code, "koto")
        area_name = area_name_map.get(area_code, f"区域{area_code}")
        type_name = type_name_map.get(property_type, "二手公寓")
        
        if property_type == "house":
            # 一户建使用不同的URL路径
            url = f"https://suumo.jp/chukoikkodate/tokyo/sc_{area_path}/"
        else:
            # 公寓使用原有的URL
            base_url = "https://suumo.jp/jj/bukken/ichiran/JJ012FC001/"
            params = f"?ar=030&bs=011&ta=13&sc={area_code}&kb=1&kt=9999999&tb=0&tt=9999999&hb=0&ht=9999999&ekTjCd=&ekTjNm=&tj=0&cnb=0&cn=9999999"
            url = base_url + params
        
        print(f"搜索条件: {area_name}（{station}附近）- {type_name}", file=sys.stderr)
        
        print(f"正在访问Suumo网站: {url}", file=sys.stderr)
        driver.get(url)
        
        # 模拟人类行为 - 等待页面加载
        time.sleep(random.uniform(2, 4))
        
        # 循环抓取多页
        for page in range(max_pages):
            print(f"正在抓取第 {page + 1} 页...", file=sys.stderr)
            
            try:
                # 等待页面完全加载
                print(f"等待页面加载...", file=sys.stderr)
                time.sleep(random.uniform(3, 5))
                
                # 等待房产列表加载（增加等待时间）
                # 不同类型的房产使用不同的class名称
                items = []
                try:
                    # 尝试1: 公寓列表页（property_unit）
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "property_unit"))
                    )
                    print(f"页面加载完成（公寓列表页）", file=sys.stderr)
                    items = driver.find_elements(By.CLASS_NAME, "property_unit")
                except:
                    try:
                        # 尝试2: 一户建列表页（property_unit-content或其他）
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".property_unit-content, .dottable-fix, .l-itemlist_item"))
                        )
                        print(f"页面加载完成（一户建/其他页面）", file=sys.stderr)
                        # 一户建可能使用不同的容器
                        items = driver.find_elements(By.CSS_SELECTOR, ".property_unit-content") or \
                                driver.find_elements(By.CLASS_NAME, "property_unit") or \
                                driver.find_elements(By.CSS_SELECTOR, ".l-itemlist_item")
                    except:
                        try:
                            # 尝试3: 租房页面
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "cassetteitem"))
                            )
                            print(f"页面加载完成（租房页面）", file=sys.stderr)
                            items = driver.find_elements(By.CLASS_NAME, "cassetteitem")
                        except:
                            print(f"⚠️  未找到房源列表，可能该地区没有此类房源", file=sys.stderr)
                            items = []
                
                print(f"找到 {len(items)} 个房产信息", file=sys.stderr)
                
                for idx, item in enumerate(items):
                    try:
                        property_data = {}
                        
                        # 判断是买房还是租房页面
                        is_sale_page = "property_unit" in item.get_attribute("class")
                        
                        if is_sale_page:
                            # 买房页面的数据提取逻辑
                            # 提取物件名称和链接
                            try:
                                title_element = item.find_element(By.CSS_SELECTOR, ".property_unit-title a")
                                building_name = title_element.text.strip()
                                property_url = title_element.get_attribute("href")
                                property_data["building_name"] = building_name
                                property_data["url"] = property_url
                                print(f"  {idx + 1}. {building_name}", file=sys.stderr)
                                print(f"     链接: {property_url}", file=sys.stderr)
                            except:
                                property_data["building_name"] = "N/A"
                                property_data["url"] = "N/A"
                            
                            # 提取价格 - 尝试多种方式
                            price = "N/A"
                            try:
                                # 方法1: 查找包含"万円"的元素
                                price_elements = item.find_elements(By.CSS_SELECTOR, "*")
                                for elem in price_elements:
                                    text = elem.text.strip()
                                    if '万円' in text and len(text) < 20:  # 价格通常很短
                                        # 清理价格格式
                                        price = text.replace('\n', ' ').replace('販売価格', '').strip()
                                        print(f"     价格: {price}", file=sys.stderr)
                                        break
                            except:
                                pass
                            property_data["price"] = price
                            
                            # 提取地址和交通信息 - 从文本中提取
                            try:
                                item_text = item.text
                                lines = [line.strip() for line in item_text.split('\n') if line.strip()]
                                
                                address = "N/A"
                                access = "N/A"
                                access_lines = []  # 收集所有可能的交通信息
                                
                                for line in lines:
                                    # 地址通常包含区名
                                    if '墨田区' in line or '区' in line:
                                        if len(line) < 50 and address == "N/A":  # 地址不会太长，取第一个
                                            address = line
                                    
                                    # 交通信息 - 更宽松的匹配条件
                                    # 1. 包含"駅"和距离信息（徒歩/分/バス等）
                                    if '駅' in line and ('歩' in line or '徒' in line or '分' in line or 'バス' in line):
                                        if len(line) < 100:  # 交通信息不会太长
                                            access_lines.append(line)
                                    # 2. 包含"駅"和"利用"或"沿線"
                                    elif '駅' in line and ('利用' in line or '沿線' in line or '路線' in line):
                                        if len(line) < 100:
                                            access_lines.append(line)
                                    # 3. 包含"アクセス"关键词
                                    elif 'アクセス' in line or '交通' in line:
                                        if len(line) < 100 and len(line) > 5:
                                            access_lines.append(line)
                                
                                # 过滤并组合交通信息
                                if access_lines:
                                    # 过滤掉无用的占位符文本
                                    filtered_access = []
                                    for acc in access_lines[:3]:
                                        # 跳过无用的标准文本
                                        if acc in ['沿線・駅', '交通', 'アクセス']:
                                            continue
                                        # 跳过太短的
                                        if len(acc) < 8:
                                            continue
                                        # 跳过标题（通常包含特殊符号和很长）
                                        if '【' in acc or '◇' in acc or '○' in acc or '■' in acc or '～' in acc:
                                            # 但是如果包含明确的駅和距离信息，保留
                                            if ('駅' in acc and '徒' in acc) or ('駅' in acc and '分' in acc and '歩' in acc):
                                                filtered_access.append(acc)
                                            continue
                                        filtered_access.append(acc)
                                    
                                    if filtered_access:
                                        access = ' / '.join(filtered_access)
                                
                                property_data["address"] = address
                                property_data["access"] = access
                                
                                if address != "N/A":
                                    print(f"     地址: {address}", file=sys.stderr)
                                if access != "N/A":
                                    print(f"     交通: {access}", file=sys.stderr)
                            except:
                                property_data["address"] = "N/A"
                                property_data["access"] = "N/A"
                            
                            # 提取建筑信息（面积、户型、建造年份等）
                            details = {}
                            area = "N/A"
                            age = "N/A"
                            layout = "N/A"
                            
                            try:
                                # 从整个item的文本中提取信息
                                item_text = item.text
                                lines = [line.strip() for line in item_text.split('\n') if line.strip()]
                                
                                for line in lines:
                                    # 提取面积（通常是XX.XXm²或XX.XX㎡）
                                    if 'm²' in line or '㎡' in line or 'ｍ²' in line or 'm2' in line:
                                        if len(line) < 30 and area == "N/A":  # 面积信息通常很短
                                            area = line
                                            details['専有面積'] = line
                                    # 也检查带有数字+平米的格式
                                    import re
                                    area_match = re.search(r'\d+\.?\d*[m㎡ｍ]', line)
                                    if area_match and len(line) < 30 and area == "N/A":
                                        area = line
                                        details['専有面積'] = line
                                    
                                    # 提取户型（1LDK, 2DK, 3LDK等）
                                    import re
                                    layout_match = re.search(r'[0-9１-９][SLDK]+', line)
                                    if layout_match and len(line) < 20:
                                        layout = layout_match.group()
                                        details['間取り'] = layout
                                    
                                    # 提取建造年份（築XX年 或 19XX年/20XX年）
                                    if '築' in line and '年' in line:
                                        age = line
                                        details['築年数'] = line
                                    elif re.search(r'(19|20)\d{2}年', line) and len(line) < 30:
                                        age = line
                                        details['築年月'] = line
                                
                                # 尝试从表格中提取（如果有）
                                try:
                                    detail_table = item.find_element(By.CSS_SELECTOR, ".dottable")
                                    rows = detail_table.find_elements(By.TAG_NAME, "tr")
                                    for row in rows:
                                        try:
                                            th = row.find_element(By.TAG_NAME, "th").text.strip()
                                            td = row.find_element(By.TAG_NAME, "td").text.strip()
                                            details[th] = td
                                            
                                            # 更新主要字段
                                            if '面積' in th:
                                                area = td
                                            if '間取' in th:
                                                layout = td
                                            if '築' in th or '建築' in th:
                                                age = td
                                        except:
                                            pass
                                except:
                                    pass
                                
                                # 显示提取到的信息
                                if idx < 3:
                                    if area != "N/A":
                                        print(f"     面积: {area}", file=sys.stderr)
                                    if layout != "N/A":
                                        print(f"     户型: {layout}", file=sys.stderr)
                                    if age != "N/A":
                                        print(f"     年限: {age}", file=sys.stderr)
                                
                            except Exception as e:
                                print(f"     提取详细信息出错: {e}", file=sys.stderr)
                            
                            property_data["details"] = details
                            property_data["area"] = area
                            property_data["layout"] = layout
                            property_data["age"] = age
                            property_data["rooms"] = []  # 买房页面通常是整套，不需要rooms数组
                            
                        else:
                            # 租房页面的数据提取逻辑（原有逻辑）
                            # 提取建筑名称和链接
                            try:
                                title_element = item.find_element(By.CLASS_NAME, "cassetteitem_content-title")
                                building_name = title_element.text
                                property_data["building_name"] = building_name
                                
                                # 提取链接 - 尝试多种方式
                                property_url = "N/A"
                                try:
                                    # 方法1: 从标题中查找链接
                                    link_element = title_element.find_element(By.TAG_NAME, "a")
                                    property_url = link_element.get_attribute("href")
                                except:
                                    try:
                                        # 方法2: 从整个item中查找第一个链接
                                        link_element = item.find_element(By.CSS_SELECTOR, "a[href*='/chintai/']")
                                        property_url = link_element.get_attribute("href")
                                    except:
                                        try:
                                            # 方法3: 查找详细按钮的链接
                                            link_element = item.find_element(By.CSS_SELECTOR, ".js-cassette_link")
                                            property_url = link_element.get_attribute("href")
                                        except:
                                            pass
                                
                                property_data["url"] = property_url
                                # if property_url != "N/A":
                                #     print(f"    链接: {property_url}", file=sys.stderr)
                            except Exception as e:
                                property_data["building_name"] = "N/A"
                                property_data["url"] = "N/A"
                                print(f"    提取标题和链接失败: {e}", file=sys.stderr)
                            
                            # 提取地址
                            try:
                                address = item.find_element(By.CLASS_NAME, "cassetteitem_detail-col1").text
                                property_data["address"] = address
                            except:
                                property_data["address"] = "N/A"
                            
                            # 提取交通信息
                            try:
                                access = item.find_element(By.CLASS_NAME, "cassetteitem_detail-text").text
                                property_data["access"] = access
                            except:
                                property_data["access"] = "N/A"
                            
                            # 提取建筑年份和结构
                            try:
                                detail_col3 = item.find_element(By.CLASS_NAME, "cassetteitem_detail-col3").text
                                property_data["building_info"] = detail_col3
                            except:
                                property_data["building_info"] = "N/A"
                            
                            # 提取发布日期/新着标记
                            publish_info = []
                            try:
                                # 查找"新着"标签
                                new_labels = item.find_elements(By.CSS_SELECTOR, ".cassetteitem_other-checkbox label")
                                for label in new_labels:
                                    label_text = label.text.strip()
                                    if label_text:
                                        publish_info.append(label_text)
                                        print(f"    标签: {label_text}", file=sys.stderr)
                            except:
                                pass
                            
                            try:
                                # 查找包含日期的元素
                                date_elements = item.find_elements(By.CSS_SELECTOR, ".ui-pct")
                                for elem in date_elements:
                                    elem_text = elem.text.strip()
                                    if '/' in elem_text or '月' in elem_text or '新着' in elem_text:
                                        publish_info.append(elem_text)
                                        print(f"    日期信息: {elem_text}", file=sys.stderr)
                            except:
                                pass
                            
                            property_data["publish_info"] = ", ".join(publish_info) if publish_info else "N/A"
                            
                            # 提取房间信息（可能有多个房间）
                            rooms = []
                            try:
                                # 尝试多种方式查找房间信息
                                room_items = item.find_elements(By.CSS_SELECTOR, "tbody tr")
                            
                                # print(f"    找到 {len(room_items)} 个房间", file=sys.stderr)
                                
                                for room_idx, room in enumerate(room_items[:3]):  # 限制每个建筑最多3个房间
                                    room_data = {}
                                    
                                    # 获取所有td元素
                                    try:
                                        cols = room.find_elements(By.TAG_NAME, "td")
                                        print(f"    房间 {room_idx + 1}: 找到 {len(cols)} 列数据", file=sys.stderr)
                                        
                                        # # 调试：显示所有列的内容
                                        # if room_idx == 0:  # 只显示第一个房间
                                        #     for i, col in enumerate(cols):
                                        #         print(f"      列{i}: {col.text.strip()[:50]}", file=sys.stderr)
                                        
                                        # 根据实际输出，列的映射如下：
                                        # 列3: 楼层
                                        if len(cols) > 2:
                                            floor = cols[2].text.strip()
                                            room_data["floor"] = floor
                                            # print(f"      楼层: {floor}", file=sys.stderr)
                                        
                                        # 列4: 租金和管理费（多行）
                                        if len(cols) > 3:
                                            price_text = cols[3].text.strip()
                                            lines = price_text.split('\n')
                                            if len(lines) >= 1:
                                                room_data["rent"] = lines[0]
                                                # print(f"      租金: {lines[0]}", file=sys.stderr)
                                            if len(lines) >= 2:
                                                room_data["admin_fee"] = lines[1]
                                                # print(f"      管理费: {lines[1]}", file=sys.stderr)
                                        
                                        # 列5: 押金/礼金（多行）
                                        if len(cols) > 4:
                                            deposit_text = cols[4].text.strip()
                                            lines = deposit_text.split('\n')
                                            if len(lines) >= 1:
                                                room_data["deposit"] = lines[0]
                                                # print(f"      押金: {lines[0]}", file=sys.stderr)
                                            if len(lines) >= 2:
                                                room_data["key_money"] = lines[1]
                                                # print(f"      礼金: {lines[1]}", file=sys.stderr)
                                        
                                        # 列6: 户型和面积（多行）
                                        if len(cols) > 5:
                                            layout_text = cols[5].text.strip()
                                            lines = layout_text.split('\n')
                                            if len(lines) >= 1:
                                                room_data["layout"] = lines[0]
                                                # print(f"      户型: {lines[0]}", file=sys.stderr)
                                            if len(lines) >= 2:
                                                room_data["area"] = lines[1]
                                                # print(f"      面积: {lines[1]}", file=sys.stderr)
                                        
                                        # 尝试提取发布日期（通常在最后一列）
                                        try:
                                            # 查找包含日期的列
                                            for col in cols:
                                                col_text = col.text.strip()
                                                # 查找包含"新着"或日期格式的文本
                                                if '新着' in col_text or '/' in col_text or '月' in col_text:
                                                    room_data["publish_info"] = col_text
                                                    print(f"      发布信息: {col_text}", file=sys.stderr)
                                                    break
                                        except:
                                            pass
                                            
                                    except Exception as e:
                                        print(f"      提取房间列数据出错: {e}", file=sys.stderr)
                                    
                                    if room_data:
                                        rooms.append(room_data)
                                        
                            except Exception as e:
                                print(f"提取房间信息时出错: {e}", file=sys.stderr)
                            
                            property_data["rooms"] = rooms
                        
                        properties.append(property_data)
                        
                        if not is_sale_page:
                            print(f"  {idx + 1}. {property_data.get('building_name', 'N/A')}", file=sys.stderr)
                        
                    except Exception as e:
                        print(f"提取房产 {idx + 1} 信息时出错: {e}", file=sys.stderr)
                        continue
                
                # 如果需要抓取多页，查找并点击下一页按钮
                if page < max_pages - 1:
                    try:
                        next_button = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
                        next_button.click()
                        time.sleep(random.uniform(2, 4))
                    except:
                        print("没有找到下一页按钮，停止抓取", file=sys.stderr)
                        break
                
            except Exception as e:
                print(f"抓取第 {page + 1} 页时出错: {e}", file=sys.stderr)
                break
        
        # 返回结果
        result = {
            "success": True,
            "data": {
                "total_properties": len(properties),
                "properties": properties,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return result
        
    except Exception as e:
        print(f"抓取过程出错: {e}", file=sys.stderr)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭", file=sys.stderr)

def extract_number(text):
    """从文本中提取数字"""
    if not text or text == 'N/A':
        return 0
    match = re.search(r'(\d+\.?\d*)', str(text))
    return float(match.group(1)) if match else 0

def upload_to_google_sheets(properties, sheet_id, station_name="", property_type_name="公寓", worksheet_name='房地产池', credentials_file='config/credentials.json', append_mode=False):
    """
    上传房源数据到Google Sheets
    
    参数:
        properties: 房源数据列表
        sheet_id: Google Sheets的ID
        station_name: 车站/地区名称（用于显示在地区列）
        property_type_name: 房屋类型名称（公寓/一户建）
        worksheet_name: 工作表名称（默认：房地产池）
        credentials_file: Google服务账号凭证文件路径
        append_mode: 是否为追加模式（True=追加，False=覆盖）
    """
    if not GSHEETS_AVAILABLE:
        print("❌ 无法上传到Google Sheets: 缺少必要的库", file=sys.stderr)
        return False
    
    try:
        print(f"\n正在准备上传到Google Sheets...", file=sys.stderr)
        print(f"目标表格ID: {sheet_id}", file=sys.stderr)
        print(f"目标工作表: {worksheet_name}", file=sys.stderr)
        
        # 认证Google Sheets API
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        print(f"正在认证...", file=sys.stderr)
        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # 打开表格
        print(f"正在打开表格...", file=sys.stderr)
        spreadsheet = client.open_by_key(sheet_id)
        print(f"表格名称: {spreadsheet.title}", file=sys.stderr)
        
        # 查找或创建工作表
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            print(f"找到工作表: {worksheet_name}", file=sys.stderr)
        except:
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
            print(f"创建新工作表: {worksheet_name}", file=sys.stderr)
        
        # 准备表头（中文+emoji，更美观）
        headers = [
            '🗺️ 地区',
            '🏘️ 类型',
            '🔢 序号',
            '🏢 物件名称', 
            '💰 价格(万円)', 
            '📊 单价(万円/m²)',
            '📏 面积(m²)',
            '🏠 户型', 
            '📅 建造年份',
            '⏳ 房龄(年)',
            '📍 地址',
            '🚇 交通',
            '🔗 详情链接',
            '⏰ 更新时间'
        ]
        
        # 准备数据行
        rows = []
        
        # 如果是追加模式，读取现有数据并检查重复
        start_row_num = 1  # 默认从第1行开始（覆盖模式）
        existing_urls = set()  # 用于去重的URL集合
        
        if append_mode:
            try:
                existing_data = worksheet.get_all_values()
                if existing_data:
                    # 检查表头是否匹配
                    if existing_data[0] != headers:
                        print(f"⚠️  表头不匹配，将覆盖现有数据", file=sys.stderr)
                        append_mode = False
                    else:
                        start_row_num = len(existing_data) + 1
                        print(f"📝 追加模式：将从第 {start_row_num} 行开始添加数据", file=sys.stderr)
                        
                        # 提取现有数据的URL（用于去重）
                        # URL在第12列（索引11）
                        url_col_idx = 11
                        for row in existing_data[1:]:  # 跳过表头
                            if len(row) > url_col_idx and row[url_col_idx]:
                                existing_urls.add(row[url_col_idx])
                        
                        print(f"📋 已有 {len(existing_urls)} 个房源URL，将自动去重", file=sys.stderr)
                else:
                    print(f"📝 工作表为空，将创建新表头", file=sys.stderr)
                    rows.append(headers)
            except:
                print(f"⚠️  读取现有数据失败，将覆盖模式", file=sys.stderr)
                append_mode = False
        
        if not append_mode:
            rows.append(headers)
        
        print(f"正在处理 {len(properties)} 个房源数据...", file=sys.stderr)
        
        # 计算序号起始值（追加模式下从现有行数继续）
        start_idx = start_row_num - 1 if append_mode else 1
        
        # 统计去重信息
        skipped_count = 0
        added_count = 0
        
        for prop in properties:
            # 检查URL是否重复（去重）
            prop_url = prop.get('url', 'N/A')
            if prop_url in existing_urls:
                skipped_count += 1
                continue  # 跳过重复的房源
            
            # 提取并清理价格（万円）
            price_text = prop.get('price', '0')
            price = 0
            
            # 处理億万円格式（如：1億980万円）
            if '億' in price_text:
                oku_match = re.search(r'(\d+)億', price_text)
                man_match = re.search(r'(\d+,?\d*)万円', price_text)
                
                oku_value = 0
                man_value = 0
                
                if oku_match:
                    oku_value = int(oku_match.group(1)) * 10000  # 1億 = 10000万
                if man_match:
                    man_value = int(man_match.group(1).replace(',', ''))
                
                price = oku_value + man_value
            else:
                # 普通格式（如：980万円）
                price_match = re.search(r'(\d+,?\d*)万円', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(',', ''))
                else:
                    price = 0
            
            # 提取并清理面积（m²）
            area_text = prop.get('area', '0')
            area = extract_number(area_text)
            
            # 计算单价（万円/m²）
            price_per_sqm = round(price / area, 2) if area > 0 and price > 0 else 0
            
            # 提取建造年份和房龄
            age_text = prop.get('age', '')
            year_match = re.search(r'(19|20)(\d{2})', age_text)
            if year_match:
                year = int(year_match.group(0))
                age_years = 2025 - year
            else:
                year = ''
                age_years = ''
            
            # 提取交通信息
            access = prop.get('access', 'N/A')
            if access and access != 'N/A':
                # 清理交通信息，提取核心部分
                access = access.strip()
            
            # 清理地址
            address = prop.get('address', 'N/A')
            if address and address != 'N/A':
                address = address.strip()
            
            # 组装数据行（添加地区列和类型列）
            current_idx = start_idx + added_count
            row = [
                station_name if station_name else 'N/A',  # 地区
                property_type_name,  # 类型（公寓/一户建）
                current_idx,  # 序号
                prop.get('building_name', 'N/A'),
                price if price > 0 else '',
                price_per_sqm if price_per_sqm > 0 else '',
                f"{area:.2f}" if area > 0 else '',
                prop.get('layout', 'N/A'),
                year if year else '',
                age_years if age_years else '',
                address,
                access,
                prop.get('url', 'N/A'),
                datetime.now().strftime('%Y-%m-%d %H:%M')
            ]
            rows.append(row)
            added_count += 1
        
        # 写入数据
        if added_count == 0 and append_mode:
            print(f"\n⚠️  所有 {len(properties)} 个房源均为重复，未添加任何新数据", file=sys.stderr)
            print(f"📋 表格保持不变", file=sys.stderr)
            return True
        
        if append_mode and start_row_num > 1:
            # 追加模式：只写入新数据
            print(f"正在追加数据（从第{start_row_num}行开始，共{added_count}个新房源）...", file=sys.stderr)
            range_name = f'A{start_row_num}'
            worksheet.update(values=rows, range_name=range_name, value_input_option='USER_ENTERED')
        else:
            # 覆盖模式：清空并重写
            print(f"正在清空工作表...", file=sys.stderr)
            worksheet.clear()
            print(f"正在写入数据...", file=sys.stderr)
            worksheet.update(values=rows, range_name='A1', value_input_option='USER_ENTERED')
        
        # 格式化表格
        print(f"正在格式化表格...", file=sys.stderr)
        
        # 1. 冻结首行（表头）
        worksheet.freeze(rows=1)
        
        # 2. 设置表头样式（粗体、背景色）
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
        
        # 3. 设置数字列格式
        total_rows = start_row_num + len(rows) - 1 if append_mode else len(rows) + 1
        if total_rows > 1:
            # 地区列 - 居中
            worksheet.format(f'A2:A{total_rows}', {
                'horizontalAlignment': 'CENTER'
            })
            
            # 类型列 - 居中
            worksheet.format(f'B2:B{total_rows}', {
                'horizontalAlignment': 'CENTER'
            })
            
            # 序号列 - 居中
            worksheet.format(f'C2:C{total_rows}', {
                'horizontalAlignment': 'CENTER'
            })
            
            # 价格列（万円）- 千位分隔符
            worksheet.format(f'E2:E{total_rows}', {
                'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'},
                'horizontalAlignment': 'RIGHT'
            })
            
            # 单价列（万円/m²）- 保留2位小数
            worksheet.format(f'F2:F{total_rows}', {
                'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0.00'},
                'horizontalAlignment': 'RIGHT'
            })
            
            # 面积列 - 保留2位小数
            worksheet.format(f'G2:G{total_rows}', {
                'numberFormat': {'type': 'NUMBER', 'pattern': '#0.00'},
                'horizontalAlignment': 'RIGHT'
            })
            
            # 建造年份和房龄 - 整数
            worksheet.format(f'I2:J{total_rows}', {
                'horizontalAlignment': 'CENTER'
            })
        
        # 4. 设置列宽（使用batch_update API）
        try:
            requests = []
            # 列宽设置（像素）
            column_widths = [
                (0, 100),  # A: 地区
                (1, 80),   # B: 类型
                (2, 80),   # C: 序号
                (3, 250),  # D: 物件名称
                (4, 120),  # E: 价格
                (5, 140),  # F: 单价
                (6, 100),  # G: 面积
                (7, 100),  # H: 户型
                (8, 110),  # I: 建造年份
                (9, 100),  # J: 房龄
                (10, 200), # K: 地址
                (11, 250), # L: 交通
                (12, 150), # M: 链接
                (13, 150), # N: 更新时间
            ]
            
            for col_idx, width in column_widths:
                requests.append({
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": col_idx,
                            "endIndex": col_idx + 1
                        },
                        "properties": {
                            "pixelSize": width
                        },
                        "fields": "pixelSize"
                    }
                })
            
            spreadsheet.batch_update({"requests": requests})
        except Exception as e:
            print(f"   ⚠️  设置列宽时出现警告: {e}", file=sys.stderr)
            print(f"   （不影响数据，表格仍可正常使用）", file=sys.stderr)
        
        # 5. 添加边框（所有数据）
        if total_rows > 1:
            worksheet.format(f'A1:N{total_rows}', {
                'borders': {
                    'top': {'style': 'SOLID', 'width': 1},
                    'bottom': {'style': 'SOLID', 'width': 1},
                    'left': {'style': 'SOLID', 'width': 1},
                    'right': {'style': 'SOLID', 'width': 1}
                }
            })
        
        print(f"\n✅ 上传成功！", file=sys.stderr)
        print(f"📊 已添加 {added_count} 个新房源", file=sys.stderr)
        if skipped_count > 0:
            print(f"⏭️  跳过 {skipped_count} 个重复房源", file=sys.stderr)
        print(f"🔗 表格链接: {spreadsheet.url}", file=sys.stderr)
        print(f"📋 工作表: {worksheet_name}", file=sys.stderr)
        
        return True
        
    except FileNotFoundError:
        print(f"\n❌ 找不到凭证文件: {credentials_file}", file=sys.stderr)
        print(f"\n请按以下步骤配置:", file=sys.stderr)
        print(f"1. 访问 https://console.cloud.google.com/", file=sys.stderr)
        print(f"2. 创建项目并启用Google Sheets API", file=sys.stderr)
        print(f"3. 创建服务账号并下载JSON密钥", file=sys.stderr)
        print(f"4. 将密钥文件保存为 {credentials_file}", file=sys.stderr)
        print(f"5. 在Google Sheets中与服务账号邮箱共享表格（编辑权限）", file=sys.stderr)
        return False
    except Exception as e:
        print(f"\n❌ 上传到Google Sheets失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

def main():
    """主函数 - 抓取指定地区的买房信息"""
    parser = argparse.ArgumentParser(description='抓取Suumo房产信息并上传到Google Sheets')
    parser.add_argument('--upload', action='store_true', 
                       help='抓取后自动上传到Google Sheets')
    parser.add_argument('--append', action='store_true',
                       help='追加模式（不清空现有数据）')
    parser.add_argument('--station', default='錦糸町',
                       help='车站/地区名称（默认：錦糸町）')
    parser.add_argument('--area-code', default='13107',
                       help='区域代码（默认：13107=墨田区，13108=江东区）')
    parser.add_argument('--type', default='mansion', choices=['mansion', 'house'],
                       help='房屋类型（mansion=公寓，house=一户建，默认：mansion）')
    parser.add_argument('--sheet-id', default='1b55-D54NLbBo1yJd-OjDy7rqCBEkK8Dza3vDLZCPaiU',
                       help='Google Sheets ID（默认：预设表格）')
    parser.add_argument('--worksheet', default='房地产池',
                       help='工作表名称（默认：房地产池）')
    parser.add_argument('--credentials', default='config/credentials.json',
                       help='Google API凭证文件路径（默认：config/credentials.json）')
    parser.add_argument('--max-pages', type=int, default=3,
                       help='最大抓取页数（默认：3）')
    parser.add_argument('--output', '-o',
                       help='保存JSON到文件（可选）')
    
    args = parser.parse_args()
    
    # 房屋类型名称映射
    type_display_names = {
        'mansion': '公寓',
        'house': '一户建'
    }
    property_type_display = type_display_names.get(args.type, '公寓')
    
    print(f"开始抓取{args.station}附近的买房信息（{property_type_display}）...", file=sys.stderr)
    
    # 抓取指定车站附近的售房信息
    result = scrape_suumo_sale(station=args.station, area_code=args.area_code, property_type=args.type, max_pages=args.max_pages)
    
    # 保存JSON到文件（如果指定）
    if args.output:
        print(f"\n正在保存数据到: {args.output}", file=sys.stderr)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已保存", file=sys.stderr)
    
    # 在stderr显示摘要
    if result.get("success"):
        print(f"\n✅ 抓取成功！", file=sys.stderr)
        print(f"📍 地点: 锦糸町附近（墨田区）", file=sys.stderr)
        print(f"🏘️  类型: 二手公寓（买房）", file=sys.stderr)
        print(f"🏠 房源数量: {result['data']['total_properties']} 个", file=sys.stderr)
        print(f"\n📝 注意: 列表页显示基本信息", file=sys.stderr)
        print(f"   可通过访问各房源的详情链接查看完整信息", file=sys.stderr)
        
        # 显示前3个房产的基本信息
        if result['data']['properties']:
            print("\n📋 前3个房源摘要:", file=sys.stderr)
            for idx, prop in enumerate(result['data']['properties'][:3], 1):
                print(f"\n{idx}. {prop.get('building_name', 'N/A')}", file=sys.stderr)
                print(f"   🔗 链接: {prop.get('url', 'N/A')}", file=sys.stderr)
                print(f"   📍 地址: {prop.get('address', 'N/A')}", file=sys.stderr)
                
                # 如果是买房信息，显示价格
                if prop.get('price'):
                    print(f"   💰 价格: {prop.get('price', 'N/A')}", file=sys.stderr)
                
                # 如果有交通信息
                if prop.get('access') and prop.get('access') != 'N/A':
                    print(f"   🚇 交通: {prop.get('access')}", file=sys.stderr)
                
                # 如果是租房信息，显示房间详情
                if prop.get('rooms') and prop['rooms']:
                    first_room = prop['rooms'][0]
                    print(f"   💰 租金: {first_room.get('rent', 'N/A')}", file=sys.stderr)
                    print(f"   🏠 户型: {first_room.get('layout', 'N/A')}", file=sys.stderr)
                    print(f"   📐 面积: {first_room.get('area', 'N/A')}", file=sys.stderr)
                
                # 显示详细信息（买房）
                if prop.get('area') and prop.get('area') != 'N/A':
                    print(f"   📐 面积: {prop['area']}", file=sys.stderr)
                if prop.get('layout') and prop.get('layout') != 'N/A':
                    print(f"   🏠 户型: {prop['layout']}", file=sys.stderr)
                if prop.get('age') and prop.get('age') != 'N/A':
                    print(f"   📅 年限: {prop['age']}", file=sys.stderr)
        
        # 如果指定了--upload参数，上传到Google Sheets
        if args.upload:
            print("\n" + "="*60, file=sys.stderr)
            properties = result['data']['properties']
            upload_success = upload_to_google_sheets(
                properties=properties,
                sheet_id=args.sheet_id,
                station_name=args.station,
                property_type_name=property_type_display,
                worksheet_name=args.worksheet,
                credentials_file=args.credentials,
                append_mode=args.append
            )
            
            if not upload_success:
                print("\n⚠️  数据已抓取但未能上传到Google Sheets", file=sys.stderr)
                print("   可以使用以下命令重试上传:", file=sys.stderr)
                print(f"   python3 scripts/suumo_scraper.py --upload --output output/suumo.json", file=sys.stderr)
        else:
            print("\n💡 提示: 使用 --upload 参数可以自动上传到Google Sheets", file=sys.stderr)
            print(f"   示例: python3 scripts/suumo_scraper.py --upload", file=sys.stderr)
    
    # 输出JSON格式结果到stdout（如果没有指定输出文件）
    if not args.output:
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

