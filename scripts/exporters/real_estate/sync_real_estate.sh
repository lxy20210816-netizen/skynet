#!/bin/bash
# 不动产数据同步脚本
# 自动抓取多个地区的房产信息并上传到Google Sheets，同时导出Markdown

# 绝对路径配置
PROJECT_DIR="/Users/a0000/Desktop/workspace/skynet"
VENV_ACTIVATE="${PROJECT_DIR}/venv/bin/activate"
SCRAPER_SCRIPT="${PROJECT_DIR}/scripts/suumo_scraper.py"
EXPORT_SCRIPT="${PROJECT_DIR}/scripts/export_real_estate.py"
SHEET_ID="1b55-D54NLbBo1yJd-OjDy7rqCBEkK8Dza3vDLZCPaiU"
WORKSHEET_NAME="房地产池"

echo "============================================================"
echo "🏘️  不动产数据同步工具"
echo "============================================================"
echo ""

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source "${VENV_ACTIVATE}"

# 定义地区和区域代码
# 格式：地区名:区域代码
declare -a LOCATIONS=(
    "錦糸町:13107"
    "亀戸:13108"
    "平井:13123"
    "秋葉原:13101"
    "高島平:13119"
    "曳舟:13107"
)

# 定义房产类型
declare -a TYPES=(
    "mansion:公寓"
    "house:一户建"
)

echo "📍 将抓取以下地区："
for location in "${LOCATIONS[@]}"; do
    IFS=':' read -r station code <<< "$location"
    echo "   - ${station} (区域代码: ${code})"
done
echo ""

echo "🏠 房产类型："
for type in "${TYPES[@]}"; do
    IFS=':' read -r type_code type_name <<< "$type"
    echo "   - ${type_name} (${type_code})"
done
echo ""

# 记录开始时间
START_TIME=$(date +%s)

# 第一次抓取（覆盖模式）
FIRST=true
TOTAL_COUNT=0
SUCCESS_COUNT=0
FAIL_COUNT=0

for location in "${LOCATIONS[@]}"; do
    IFS=':' read -r station code <<< "$location"
    
    for type in "${TYPES[@]}"; do
        IFS=':' read -r type_code type_name <<< "$type"
        
        TOTAL_COUNT=$((TOTAL_COUNT + 1))
        
        echo "----------------------------------------"
        echo "📥 正在抓取: ${station} - ${type_name}"
        echo "----------------------------------------"
        
        # 构建命令
        if [ "$FIRST" = true ]; then
            # 第一次不使用--append（覆盖模式）
            CMD="python3 ${SCRAPER_SCRIPT} --upload --station ${station} --area-code ${code} --type ${type_code} --max-pages 1"
            FIRST=false
        else
            # 后续使用--append（追加模式）
            CMD="python3 ${SCRAPER_SCRIPT} --upload --append --station ${station} --area-code ${code} --type ${type_code} --max-pages 1"
        fi
        
        # 执行抓取
        if eval "$CMD"; then
            echo "✅ ${station} - ${type_name} 抓取成功"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo "❌ ${station} - ${type_name} 抓取失败"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
        
        echo ""
        
        # 短暂延迟，避免过快请求
        sleep 2
    done
done

echo "============================================================"
echo "📊 抓取统计"
echo "============================================================"
echo "总任务数: ${TOTAL_COUNT}"
echo "成功: ${SUCCESS_COUNT}"
echo "失败: ${FAIL_COUNT}"
echo ""

# 计算耗时
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))
echo "⏱️  总耗时: ${MINUTES}分${SECONDS}秒"
echo ""

# 导出Markdown
echo "============================================================"
echo "📄 导出Markdown文档"
echo "============================================================"
echo ""

if python3 "${EXPORT_SCRIPT}"; then
    echo "✅ Markdown导出成功"
else
    echo "❌ Markdown导出失败"
    exit 1
fi

echo ""
echo "============================================================"
echo "🎉 全部完成！"
echo "============================================================"
echo ""
echo "📊 Google Sheets: https://docs.google.com/spreadsheets/d/${SHEET_ID}"
echo "📄 本地Markdown: /Users/a0000/Desktop/workspace/brain/不动产池/不动产池.md"
echo ""

