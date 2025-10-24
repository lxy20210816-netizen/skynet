#!/bin/bash

# 快速开始脚本 - 抓取指定地区的房产信息
# 这是一个简化的使用示例

set -e

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BATCH_SCRIPT="$SCRIPT_DIR/batch_scrape.sh"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🏠 房产信息批量抓取工具${NC}"
echo "=================================="
echo

# 显示菜单
show_menu() {
    echo "请选择要抓取的地区："
    echo "1) 錦糸町 (墨田区)"
    echo "2) 亀戸 (江东区)" 
    echo "3) 秋葉原 (千代田区)"
    echo "4) 渋谷 (世田谷区)"
    echo "5) 上野 (千代田区)"
    echo "6) 浅草寺 (墨田区)"
    echo "7) 平井 (墨田区)"
    echo "8) 高島平 (板桥区)"
    echo "9) 板橋区役所前 (板桥区)"
    echo "10) 所有地区"
    echo "0) 退出"
    echo
}

# 根据选择执行抓取
execute_scrape() {
    local choice="$1"
    
    case "$choice" in
        1) 
            echo -e "${GREEN}开始抓取錦糸町的房产信息...${NC}"
            "$BATCH_SCRIPT" -s "kinshicho"
            ;;
        2)
            echo -e "${GREEN}开始抓取亀戸的房产信息...${NC}"
            "$BATCH_SCRIPT" -s "kameido"
            ;;
        3)
            echo -e "${GREEN}开始抓取秋葉原的房产信息...${NC}"
            "$BATCH_SCRIPT" -s "akihabara"
            ;;
        4)
            echo -e "${GREEN}开始抓取渋谷的房产信息...${NC}"
            "$BATCH_SCRIPT" -s "shibuya"
            ;;
        5)
            echo -e "${GREEN}开始抓取上野的房产信息...${NC}"
            "$BATCH_SCRIPT" -s "ueno"
            ;;
        6)
            echo -e "${GREEN}开始抓取浅草寺的房产信息...${NC}"
            "$BATCH_SCRIPT" -s "asakusa"
            ;;
        7)
            echo -e "${GREEN}开始抓取平井的房产信息...${NC}"
            "$BATCH_SCRIPT" -s "hirai"
            ;;
        8)
            echo -e "${GREEN}开始抓取高島平的房产信息...${NC}"
            "$BATCH_SCRIPT" -s "takashimadaira"
            ;;
        9)
            echo -e "${GREEN}开始抓取板橋区役所前的房产信息...${NC}"
            "$BATCH_SCRIPT" -s "itabashikuyakusho"
            ;;
        10)
            echo -e "${GREEN}开始抓取所有地区的房产信息...${NC}"
            echo "注意：这将需要较长时间（约15-20分钟）"
            read -p "确认继续？(y/N): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                "$BATCH_SCRIPT"
            else
                echo "已取消"
                exit 0
            fi
            ;;
        0)
            echo "退出"
            exit 0
            ;;
        *)
            echo "无效选择，请重新输入"
            return 1
            ;;
    esac
}

# 主循环
while true; do
    show_menu
    read -p "请输入选择 (0-10): " choice
    
    if execute_scrape "$choice"; then
        echo
        echo -e "${GREEN}✅ 抓取完成！${NC}"
        echo "数据已上传到Google Sheets"
        echo "输出文件保存在: output/"
        echo "日志文件保存在: logs/"
        echo
        read -p "是否继续抓取其他地区？(y/N): " continue_choice
        if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
            break
        fi
    fi
done

echo "感谢使用！"
