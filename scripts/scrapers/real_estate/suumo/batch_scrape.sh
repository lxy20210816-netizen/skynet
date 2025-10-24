#!/bin/bash

# 批量抓取多个地区的房产信息脚本
# 支持二手公寓和一户建信息抓取并上传到Google Sheets

set -e  # 遇到错误立即退出

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SUUMO_SCRIPT="$SCRIPT_DIR/suumo_scraper.py"
OUTPUT_DIR="$PROJECT_ROOT/output"
LOG_DIR="$PROJECT_ROOT/logs"

# 创建必要的目录
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 地区配置 - 使用函数方式避免关联数组
get_station_code() {
    case "$1" in
        "kinshicho") echo "13107" ;;      # 錦糸町 - 墨田区
        "hirai") echo "13107" ;;          # 平井 - 墨田区
        "kameido") echo "13108" ;;        # 亀戸 - 江东区
        "takashimadaira") echo "13119" ;; # 高島平 - 板桥区
        "itabashikuyakusho") echo "13119" ;; # 板橋区役所前 - 板桥区
        "akihabara") echo "13101" ;;      # 秋葉原 - 千代田区
        "shibuya") echo "13112" ;;        # 渋谷 - 世田谷区
        "ueno") echo "13101" ;;           # 上野 - 千代田区
        "asakusa") echo "13107" ;;        # 浅草寺 - 墨田区
        *) echo "" ;;
    esac
}

get_station_name() {
    case "$1" in
        "kinshicho") echo "錦糸町" ;;
        "hirai") echo "平井" ;;
        "kameido") echo "亀戸" ;;
        "takashimadaira") echo "高島平" ;;
        "itabashikuyakusho") echo "板橋区役所前" ;;
        "akihabara") echo "秋葉原" ;;
        "shibuya") echo "渋谷" ;;
        "ueno") echo "上野" ;;
        "asakusa") echo "浅草寺" ;;
        *) echo "$1" ;;
    esac
}

get_area_name() {
    case "$1" in
        "13107") echo "墨田区" ;;
        "13108") echo "江东区" ;;
        "13119") echo "板桥区" ;;
        "13101") echo "千代田区" ;;
        "13112") echo "世田谷区" ;;
        *) echo "未知区域" ;;
    esac
}

# 获取所有配置的地区
get_all_stations() {
    echo "kinshicho hirai kameido takashimadaira itabashikuyakusho akihabara shibuya ueno asakusa"
}

# 检查Python环境
check_python() {
    log_info "检查Python环境..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装或不在PATH中"
        exit 1
    fi
    
    # 检查必要的Python包
    python3 -c "import selenium, gspread" 2>/dev/null || {
        log_error "缺少必要的Python包，请运行: pip install selenium gspread google-auth"
        exit 1
    }
    
    log_success "Python环境检查通过"
}

# 检查suumo_scraper.py脚本
check_script() {
    log_info "检查suumo_scraper.py脚本..."
    if [[ ! -f "$SUUMO_SCRIPT" ]]; then
        log_error "找不到suumo_scraper.py脚本: $SUUMO_SCRIPT"
        exit 1
    fi
    
    if [[ ! -x "$SUUMO_SCRIPT" ]]; then
        log_warning "suumo_scraper.py脚本没有执行权限，正在添加..."
        chmod +x "$SUUMO_SCRIPT"
    fi
    
    log_success "脚本检查通过"
}

# 抓取单个地区的房产信息
scrape_area() {
    local station_key="$1"
    local area_code="$2"
    local station_name=$(get_station_name "$station_key")
    local area_name=$(get_area_name "$area_code")
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    
    log_info "开始抓取 $station_name ($area_name) 的房产信息..."
    
    # 抓取二手公寓
    log_info "抓取 $station_name 的二手公寓信息..."
    local apartment_output="$OUTPUT_DIR/suumo_${station_key}_apartment_${timestamp}.json"
    local apartment_log="$LOG_DIR/suumo_${station_key}_apartment_${timestamp}.log"
    
    if python3 "$SUUMO_SCRIPT" \
        --upload \
        --station "$station_name" \
        --area-code "$area_code" \
        --type mansion \
        --worksheet "房地产池" \
        --max-pages 3 \
        --append \
        --output "$apartment_output" \
        > "$apartment_log" 2>&1; then
        log_success "$station_name 二手公寓抓取成功"
    else
        log_error "$station_name 二手公寓抓取失败，查看日志: $apartment_log"
        return 1
    fi
    
    # 等待一段时间避免请求过于频繁
    sleep 5
    
    # 抓取一户建
    log_info "抓取 $station_name 的一户建信息..."
    local house_output="$OUTPUT_DIR/suumo_${station_key}_house_${timestamp}.json"
    local house_log="$LOG_DIR/suumo_${station_key}_house_${timestamp}.log"
    
    if python3 "$SUUMO_SCRIPT" \
        --upload \
        --station "$station_name" \
        --area-code "$area_code" \
        --type house \
        --worksheet "房地产池" \
        --max-pages 3 \
        --append \
        --output "$house_output" \
        > "$house_log" 2>&1; then
        log_success "$station_name 一户建抓取成功"
    else
        log_error "$station_name 一户建抓取失败，查看日志: $house_log"
        return 1
    fi
    
    # 等待一段时间避免请求过于频繁
    sleep 5
    
    return 0
}

# 显示帮助信息
show_help() {
    cat << EOF
批量抓取多个地区的房产信息脚本

用法:
    $0 [选项]

选项:
    -h, --help              显示此帮助信息
    -s, --stations STATIONS 指定要抓取的地区（逗号分隔）
    -a, --apartment-only    只抓取二手公寓
    --house-only            只抓取一户建
    -d, --dry-run           试运行模式（不实际上传）
    -v, --verbose           详细输出

示例:
    $0                                    # 抓取所有配置的地区
    $0 -s "kinshicho,kameido,akihabara"  # 只抓取指定地区
    $0 -a                                  # 只抓取二手公寓
    $0 --house-only                        # 只抓取一户建

配置的地区:
    錦糸町 (墨田区)
    平井 (墨田区)
    亀戸 (江东区)
    高島平 (板桥区)
    板橋区役所前 (板桥区)
    秋葉原 (千代田区)
    渋谷 (世田谷区)
    上野 (千代田区)
    浅草寺 (墨田区)

输出目录: $OUTPUT_DIR
日志目录: $LOG_DIR
EOF
}

# 主函数
main() {
    local stations_to_scrape=()
    local apartment_only=false
    local house_only=false
    local dry_run=false
    local verbose=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--stations)
                IFS=',' read -ra stations_to_scrape <<< "$2"
                shift 2
                ;;
            -a|--apartment-only)
                apartment_only=true
                shift
                ;;
            --house-only)
                house_only=true
                shift
                ;;
            -d|--dry-run)
                dry_run=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果没有指定地区，使用所有配置的地区
    if [[ ${#stations_to_scrape[@]} -eq 0 ]]; then
        stations_to_scrape=($(get_all_stations))
    fi
    
    log_info "开始批量抓取房产信息..."
    log_info "目标地区: ${stations_to_scrape[*]}"
    log_info "抓取类型: $([ "$apartment_only" = true ] && echo "仅二手公寓" || [ "$house_only" = true ] && echo "仅一户建" || echo "二手公寓+一户建")"
    
    if [[ "$dry_run" = true ]]; then
        log_warning "试运行模式，不会实际上传数据"
    fi
    
    # 检查环境
    check_python
    check_script
    
    # 统计变量
    local total_areas=${#stations_to_scrape[@]}
    local success_count=0
    local failed_areas=()
    
    # 开始抓取
    local start_time=$(date +%s)
    
    for station_key in "${stations_to_scrape[@]}"; do
        local area_code=$(get_station_code "$station_key")
        if [[ -z "$area_code" ]]; then
            log_error "未配置的地区: $station_key"
            failed_areas+=("$station_key")
            continue
        fi
        
        local station_name=$(get_station_name "$station_key")
        local area_name=$(get_area_name "$area_code")
        
        log_info "处理地区: $station_name ($area_name)"
        
        if [[ "$dry_run" = true ]]; then
            log_info "[试运行] 将抓取 $station_name 的房产信息"
            success_count=$((success_count + 1))
            continue
        fi
        
        if scrape_area "$station_key" "$area_code"; then
            success_count=$((success_count + 1))
            log_success "$station_name 抓取完成"
        else
            failed_areas+=("$station_name")
            log_error "$station_name 抓取失败"
        fi
        
        # 在地区之间等待更长时间
        if [[ $success_count -lt $total_areas ]]; then
            log_info "等待30秒后继续下一个地区..."
            sleep 30
        fi
    done
    
    # 显示最终结果
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    echo
    log_info "=== 抓取完成 ==="
    log_info "总地区数: $total_areas"
    log_success "成功: $success_count"
    
    if [[ ${#failed_areas[@]} -gt 0 ]]; then
        log_error "失败: ${#failed_areas[@]}"
        log_error "失败地区: ${failed_areas[*]}"
    fi
    
    log_info "总耗时: ${minutes}分${seconds}秒"
    
    if [[ "$dry_run" = false ]]; then
        log_info "数据已上传到Google Sheets"
        log_info "输出文件保存在: $OUTPUT_DIR"
        log_info "日志文件保存在: $LOG_DIR"
    fi
    
    # 返回适当的退出码
    if [[ ${#failed_areas[@]} -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# 运行主函数
main "$@"