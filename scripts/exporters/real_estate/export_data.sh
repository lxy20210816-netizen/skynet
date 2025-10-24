#!/bin/bash

# 从Google Sheets导出房产数据到本地文件夹
# 目标文件夹: /Users/a0000/Desktop/workspace/brain/skynet

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
EXPORT_SCRIPT="$SCRIPT_DIR/export_from_gsheets.py"
TARGET_DIR="/Users/a0000/Desktop/workspace/brain/skynet"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
从Google Sheets导出房产数据到本地文件夹

用法:
    $0 [选项]

选项:
    -h, --help              显示此帮助信息
    -d, --dir DIR           指定输出目录（默认：/Users/a0000/Desktop/workspace/brain/skynet）
    -f, --formats FORMATS   指定导出格式（默认：json,csv,excel）
    -s, --sheet-id ID       指定Google Sheets ID
    -w, --worksheet NAME    指定工作表名称（默认：房地产池）

示例:
    $0                                    # 导出到默认目录
    $0 -d /path/to/output                 # 导出到指定目录
    $0 -f json,csv                        # 只导出JSON和CSV格式
    $0 -s "your_sheet_id"                 # 指定表格ID

支持的格式:
    json    - JSON格式（包含元数据）
    csv     - CSV格式（Excel兼容）
    excel   - Excel格式（.xlsx）

目标目录: $TARGET_DIR
EOF
}

# 检查Python环境
check_python() {
    log_info "检查Python环境..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装或不在PATH中"
        exit 1
    fi
    
    # 检查必要的Python包
    python3 -c "import gspread, pandas" 2>/dev/null || {
        log_error "缺少必要的Python包，请运行: pip install gspread google-auth pandas openpyxl"
        exit 1
    }
    
    log_success "Python环境检查通过"
}

# 检查目标目录
check_target_dir() {
    local target_dir="$1"
    
    log_info "检查目标目录: $target_dir"
    
    if [[ ! -d "$target_dir" ]]; then
        log_info "目标目录不存在，正在创建..."
        mkdir -p "$target_dir"
        if [[ $? -eq 0 ]]; then
            log_success "目标目录创建成功"
        else
            log_error "无法创建目标目录: $target_dir"
            exit 1
        fi
    else
        log_success "目标目录存在"
    fi
    
    # 检查写入权限
    if [[ -w "$target_dir" ]]; then
        log_success "目标目录可写"
    else
        log_error "目标目录无写入权限: $target_dir"
        exit 1
    fi
}

# 执行导出
execute_export() {
    local output_dir="$1"
    local formats="$2"
    local sheet_id="$3"
    local worksheet="$4"
    
    log_info "开始从Google Sheets导出数据..."
    log_info "输出目录: $output_dir"
    log_info "导出格式: $formats"
    log_info "表格ID: $sheet_id"
    log_info "工作表: $worksheet"
    
    # 执行Python导出脚本
    if python3 "$EXPORT_SCRIPT" \
        --output-dir "$output_dir" \
        --formats $formats \
        --sheet-id "$sheet_id" \
        --worksheet "$worksheet"; then
        log_success "数据导出成功"
        return 0
    else
        log_error "数据导出失败"
        return 1
    fi
}

# 显示导出结果
show_results() {
    local output_dir="$1"
    
    echo
    log_info "=== 导出结果 ==="
    
    if [[ -d "$output_dir" ]]; then
        log_info "输出目录: $output_dir"
        
        # 显示文件列表
        local file_count=$(find "$output_dir" -name "real_estate_data_*.json" -o -name "real_estate_data_*.csv" -o -name "real_estate_data_*.xlsx" | wc -l)
        log_info "生成文件数: $file_count"
        
        # 显示最新文件
        echo
        log_info "最新文件:"
        find "$output_dir" -name "real_estate_data_*" -type f -exec ls -la {} \; | tail -5
        
        # 显示数据摘要
        local summary_file=$(find "$output_dir" -name "data_summary_*.txt" | sort | tail -1)
        if [[ -f "$summary_file" ]]; then
            echo
            log_info "数据摘要:"
            cat "$summary_file"
        fi
    else
        log_warning "输出目录不存在"
    fi
}

# 主函数
main() {
    local output_dir="$TARGET_DIR"
    local formats="json csv excel"
    local sheet_id="1b55-D54NLbBo1yJd-OjDy7rqCBEkK8Dza3vDLZCPaiU"
    local worksheet="房地产池"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--dir)
                output_dir="$2"
                shift 2
                ;;
            -f|--formats)
                formats="$2"
                shift 2
                ;;
            -s|--sheet-id)
                sheet_id="$2"
                shift 2
                ;;
            -w|--worksheet)
                worksheet="$2"
                shift 2
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo -e "${BLUE}🏠 房地产数据导出工具${NC}"
    echo "=================================="
    echo
    
    # 检查环境
    check_python
    check_target_dir "$output_dir"
    
    # 执行导出
    if execute_export "$output_dir" "$formats" "$sheet_id" "$worksheet"; then
        show_results "$output_dir"
        log_success "导出完成！"
        exit 0
    else
        log_error "导出失败"
        exit 1
    fi
}

# 运行主函数
main "$@"
