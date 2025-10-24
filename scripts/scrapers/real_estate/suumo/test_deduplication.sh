#!/bin/bash

# 测试去重功能的脚本
# 抓取少量数据来测试去重逻辑

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUUMO_SCRIPT="$SCRIPT_DIR/suumo_scraper.py"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧪 测试去重功能${NC}"
echo "=================================="
echo

# 测试1: 抓取錦糸町的少量数据
echo -e "${YELLOW}测试1: 抓取錦糸町的公寓数据（第1次）${NC}"
python3 "$SUUMO_SCRIPT" \
    --upload \
    --station "錦糸町" \
    --area-code "13107" \
    --type mansion \
    --worksheet "房地产池" \
    --max-pages 1 \
    --append

echo
echo "等待5秒..."
sleep 5

# 测试2: 再次抓取相同数据（应该被去重）
echo -e "${YELLOW}测试2: 再次抓取錦糸町的公寓数据（第2次，应该去重）${NC}"
python3 "$SUUMO_SCRIPT" \
    --upload \
    --station "錦糸町" \
    --area-code "13107" \
    --type mansion \
    --worksheet "房地产池" \
    --max-pages 1 \
    --append

echo
echo "等待5秒..."
sleep 5

# 测试3: 抓取不同地区的数据（应该正常添加）
echo -e "${YELLOW}测试3: 抓取亀戸的公寓数据（不同地区，应该正常添加）${NC}"
python3 "$SUUMO_SCRIPT" \
    --upload \
    --station "亀戸" \
    --area-code "13108" \
    --type mansion \
    --worksheet "房地产池" \
    --max-pages 1 \
    --append

echo
echo -e "${GREEN}✅ 去重功能测试完成！${NC}"
echo "请检查Google Sheets中的数据："
echo "1. 錦糸町的数据应该只出现一次"
echo "2. 亀戸的数据应该正常添加"
echo "3. 控制台应该显示跳过的重复记录"
