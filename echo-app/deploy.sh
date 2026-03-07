#!/bin/bash

# ==========================================
# 回响 - 一键部署脚本
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        log_info "安装命令（Ubuntu/Debian）: curl -fsSL https://get.docker.com | sh"
        log_info "安装命令（CentOS）: yum install -y docker-ce docker-ce-cli containerd.io"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi

    log_success "Docker 环境检查通过"
}

# 检查环境变量文件
check_env() {
    if [ ! -f "backend/.env" ]; then
        log_warn "backend/.env 文件不存在，正在从模板创建..."
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            log_info "已创建 backend/.env，请编辑填入真实的 API Key"
        else
            log_error "找不到 backend/.env.example 模板文件"
            exit 1
        fi
    fi
    log_success "环境变量文件检查通过"
}

# 创建数据目录
create_dirs() {
    log_info "创建数据目录..."
    mkdir -p data
    mkdir -p nginx/ssl
    log_success "目录创建完成"
}

# 构建镜像
build() {
    log_info "开始构建 Docker 镜像..."

    # 判断使用 docker-compose 还是 docker compose
    if command -v docker-compose &> /dev/null; then
        docker-compose build --no-cache
    else
        docker compose build --no-cache
    fi

    log_success "镜像构建完成"
}

# 启动服务
start() {
    log_info "启动服务..."

    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi

    log_success "服务启动完成"
    log_info "访问地址: http://localhost"
}

# 停止服务
stop() {
    log_info "停止服务..."

    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi

    log_success "服务已停止"
}

# 查看日志
logs() {
    if command -v docker-compose &> /dev/null; then
        docker-compose logs -f
    else
        docker compose logs -f
    fi
}

# 重启服务
restart() {
    stop
    start
}

# 更新部署
update() {
    log_info "拉取最新代码并重新部署..."
    git pull || log_warn "git pull 失败，继续使用当前代码"
    build
    restart
    log_success "更新完成"
}

# 查看状态
status() {
    log_info "服务状态:"
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
}

# 帮助信息
help() {
    echo "
回响 - 一键部署脚本

用法: ./deploy.sh [命令]

命令:
  check     检查环境（Docker、env 文件）
  build     构建 Docker 镜像
  start     启动服务
  stop      停止服务
  restart   重启服务
  logs      查看日志
  status    查看服务状态
  update    拉取最新代码并重新部署
  all       完整部署（check + build + start）
  help      显示帮助信息

示例:
  ./deploy.sh all       # 首次部署
  ./deploy.sh update    # 更新部署
  ./deploy.sh logs      # 查看日志
"
}

# 主函数
main() {
    cd "$(dirname "$0")"

    case "${1:-help}" in
        check)
            check_docker
            check_env
            create_dirs
            ;;
        build)
            check_docker
            build
            ;;
        start)
            check_docker
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs
            ;;
        status)
            status
            ;;
        update)
            check_docker
            update
            ;;
        all)
            log_info "========== 开始完整部署 =========="
            check_docker
            check_env
            create_dirs
            build
            start
            status
            log_success "========== 部署完成 =========="
            log_info "访问地址: http://$(hostname -I | awk '{print $1}')"
            ;;
        help|--help|-h)
            help
            ;;
        *)
            log_error "未知命令: $1"
            help
            exit 1
            ;;
    esac
}

main "$@"
