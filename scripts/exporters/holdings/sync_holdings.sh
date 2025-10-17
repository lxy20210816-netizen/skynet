#!/bin/bash
# 同步持仓明细数据到本地
# 从Google Sheets读取"资产明细"并保存为Markdown格式

# 绝对路径配置
PROJECT_DIR="/Users/a0000/Desktop/workspace/skynet"
VENV_ACTIVATE="${PROJECT_DIR}/venv/bin/activate"
PYTHON_SCRIPT="${PROJECT_DIR}/scripts/export_holdings.py"
OUTPUT_DIR="/Users/a0000/Desktop/workspace/brain/1-现状"
OUTPUT_FILE="${OUTPUT_DIR}/我的持仓.md"

echo "============================================================"
echo "💼 持仓明细同步工具"
echo "============================================================"
echo ""

# 创建输出目录（如果不存在）
mkdir -p "${OUTPUT_DIR}"

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source "${VENV_ACTIVATE}"

# 运行Python脚本并保存输出
echo "📥 正在从Google Sheets读取持仓明细..."
python3 "${PYTHON_SCRIPT}" > "${OUTPUT_FILE}" 2>&1

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 持仓明细已成功保存！"
    echo "📂 文件位置: ${OUTPUT_FILE}"
    echo ""
    
    # 显示文件大小和行数
    FILE_SIZE=$(ls -lh "${OUTPUT_FILE}" | awk '{print $5}')
    LINE_COUNT=$(wc -l < "${OUTPUT_FILE}")
    
    echo "📊 文件信息:"
    echo "   - 大小: ${FILE_SIZE}"
    echo "   - 行数: ${LINE_COUNT}"
    echo ""
    echo "💡 提示: 可以用任何Markdown编辑器打开查看"
    echo "   例如: open \"${OUTPUT_FILE}\""
else
    echo ""
    echo "❌ 同步失败，请检查错误信息"
    exit 1
fi

