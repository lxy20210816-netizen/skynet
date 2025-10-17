#!/bin/bash
# 朝日新闻RSS抓取脚本
# 自动抓取朝日新闻RSS feed并保存为JSON

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="/Users/a0000/Desktop/workspace/skynet"
SCRIPT_PATH="${PROJECT_DIR}/scripts/fetch_asahi_rss.py"
OUTPUT_DIR="/Users/a0000/Desktop/workspace/brain/skynet"
VENV_DIR="${PROJECT_DIR}/venv"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}📰 朝日新闻RSS同步工具${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ 虚拟环境不存在: $VENV_DIR${NC}"
    exit 1
fi

# 激活虚拟环境
echo -e "${YELLOW}🔧 激活虚拟环境...${NC}"
source "${VENV_DIR}/bin/activate"

# 检查依赖
echo -e "${YELLOW}🔍 检查依赖...${NC}"
python3 -c "import feedparser, requests" 2>/dev/null || {
    echo -e "${YELLOW}📦 安装依赖...${NC}"
    pip install feedparser requests -q
}

# 运行脚本
echo -e "${GREEN}🚀 开始抓取新闻...${NC}"
echo ""

cd "$PROJECT_DIR"
python3 "$SCRIPT_PATH" 2>&1 | tee /tmp/asahi_rss_sync.log

# 检查执行结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}✅ 同步完成！${NC}"
    echo -e "${GREEN}============================================================${NC}"
    
    # 显示输出文件信息
    TODAY=$(date +%Y%m%d)
    OUTPUT_FILE="${OUTPUT_DIR}/asahi_newsheadlines_${TODAY}.json"
    
    if [ -f "$OUTPUT_FILE" ]; then
        FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
        NEWS_COUNT=$(grep -o '"id":' "$OUTPUT_FILE" | wc -l | xargs)
        
        echo ""
        echo -e "${BLUE}📂 文件信息:${NC}"
        echo -e "   路径: ${OUTPUT_FILE}"
        echo -e "   大小: ${FILE_SIZE}"
        echo -e "   数量: ${NEWS_COUNT} 条新闻"
        echo ""
        
        # 显示前3条新闻标题
        echo -e "${BLUE}📰 最新新闻预览:${NC}"
        python3 -c "
import json
with open('$OUTPUT_FILE', 'r', encoding='utf-8') as f:
    news = json.load(f)
    for item in news[:3]:
        print(f\"   {item['id']}. {item['title']}\")
        print(f\"      {item['pubDate']}\")
" 2>/dev/null || echo "   (无法读取)"
        echo ""
    fi
else
    echo ""
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}❌ 同步失败！${NC}"
    echo -e "${RED}============================================================${NC}"
    echo ""
    echo -e "${YELLOW}请查看日志: /tmp/asahi_rss_sync.log${NC}"
    exit 1
fi

# 退出虚拟环境
deactivate

