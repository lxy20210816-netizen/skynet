#!/usr/bin/env python3
"""
Suumo房地产信息抓取脚本
使用Selenium抓取Suumo网站的房产信息
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
from datetime import datetime

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

def scrape_suumo_sale(station="錦糸町", max_pages=3):
    """
    抓取Suumo售房信息 - 锦糸町附近的买房信息
    
    参数:
        station: 车站名称（如：錦糸町）
        max_pages: 最大抓取页数
    """
    driver = None
    properties = []
    
    try:
        driver = setup_driver()
        if not driver:
            return {"success": False, "error": "浏览器启动失败"}
        
        # 锦糸町车站附近的售房信息URL - 墨田区
        # ar=030: 関東
        # bs=011: 中古マンション（二手公寓）
        # ta=13: 東京都
        # sc=13107: 墨田区
        base_url = "https://suumo.jp/jj/bukken/ichiran/JJ012FC001/"
        params = "?ar=030&bs=011&ta=13&sc=13107&kb=1&kt=9999999&tb=0&tt=9999999&hb=0&ht=9999999&ekTjCd=&ekTjNm=&tj=0&cnb=0&cn=9999999"
        url = base_url + params
        
        print(f"搜索条件: 墨田区（锦糸町所在区）- 二手公寓", file=sys.stderr)
        
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
                # 买房页面使用不同的class名称
                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "property_unit"))
                    )
                    print(f"页面加载完成（买房页面）", file=sys.stderr)
                    items = driver.find_elements(By.CLASS_NAME, "property_unit")
                except:
                    # 如果是租房页面
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "cassetteitem"))
                    )
                    print(f"页面加载完成", file=sys.stderr)
                    items = driver.find_elements(By.CLASS_NAME, "cassetteitem")
                
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
                                
                                for line in lines:
                                    # 地址通常包含区名
                                    if '墨田区' in line or '区' in line:
                                        if len(line) < 50:  # 地址不会太长
                                            address = line
                                    # 交通信息通常包含"駅"或"分"
                                    if '駅' in line and '歩' in line:
                                        access = line
                                
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

def main():
    """主函数 - 抓取锦糸町附近的买房信息"""
    print("开始抓取锦糸町附近的买房信息（二手公寓）...", file=sys.stderr)
    
    # 抓取锦糸町车站附近的售房信息
    result = scrape_suumo_sale(station="錦糸町", max_pages=3)
    
    # 输出JSON格式结果（只输出JSON，不包含调试信息）
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 在stderr显示摘要（不影响JSON输出）
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

if __name__ == "__main__":
    main()

