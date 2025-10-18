#!/bin/bash
# 同步雪球用户发文
# 抓取段永平（大道无形我有型）的雪球发文并保存

# 绝对路径配置
PROJECT_DIR="$HOME/Desktop/workspace/skynet"
VENV_ACTIVATE="${PROJECT_DIR}/venv/bin/activate"
PYTHON_SCRIPT="${PROJECT_DIR}/scripts/xueqiu_scraper.py"
OUTPUT_DIR="${PROJECT_DIR}/output"
OUTPUT_FILE="${OUTPUT_DIR}/xueqiu_duanyongping.json"
MD_FILE="${OUTPUT_DIR}/xueqiu_duanyongping.md"

# 段永平的雪球用户ID
# 用户主页格式：https://xueqiu.com/u/[USER_ID]
USER_ID="9528875558"  # 段永平（大道无形我有型）

echo "============================================================"
echo "📊 雪球发文同步工具"
echo "============================================================"
echo ""
echo "👤 目标用户: 段永平（大道无形我有型）"
echo "🆔 用户ID: ${USER_ID}"
echo ""

# 创建输出目录（如果不存在）
mkdir -p "${OUTPUT_DIR}"

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source "${VENV_ACTIVATE}"

# 检查是否安装了selenium
echo "🔍 检查依赖..."
python3 -c "import selenium" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 未安装selenium，正在安装..."
    pip install selenium
fi

# 运行爬虫脚本
echo "🕷️  开始抓取雪球发文..."
echo ""

# 使用支持登录的版本
PYTHON_SCRIPT="${PROJECT_DIR}/scripts/xueqiu_with_login.py"

python3 "${PYTHON_SCRIPT}" \
    --user-id "${USER_ID}" \
    --max-posts 50 \
    --output "${OUTPUT_FILE}" \
    --format both \
    --visible

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 雪球发文已成功抓取！"
    echo ""
    echo "📂 文件位置:"
    echo "   - JSON: ${OUTPUT_FILE}"
    echo "   - Markdown: ${MD_FILE}"
    echo ""
    
    # 显示文件信息
    if [ -f "${OUTPUT_FILE}" ]; then
        FILE_SIZE=$(ls -lh "${OUTPUT_FILE}" | awk '{print $5}')
        POST_COUNT=$(python3 -c "import json; print(len(json.load(open('${OUTPUT_FILE}'))))" 2>/dev/null)
        
        echo "📊 抓取统计:"
        echo "   - 文件大小: ${FILE_SIZE}"
        echo "   - 发文数量: ${POST_COUNT}条"
        echo ""
    fi
    
    echo "💡 提示:"
    echo "   - 查看JSON: cat \"${OUTPUT_FILE}\""
    echo "   - 查看Markdown: open \"${MD_FILE}\""
else
    echo ""
    echo "❌ 抓取失败，请检查错误信息"
    echo ""
    echo "💡 常见问题："
    echo "   1. 用户ID是否正确？访问 https://xueqiu.com 搜索用户"
    echo "   2. 是否安装了Chrome浏览器？"
    echo "   3. 网络连接是否正常？"
    exit 1
fi

