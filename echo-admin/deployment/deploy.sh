#!/bin/bash
# 回响后台管理系统 - 部署脚本

set -e

echo "======================================"
echo "回响后台管理系统 - 部署脚本"
echo "======================================"

# 配置变量
PROJECT_DIR="/opt/echo-admin"
BACKUP_DIR="/opt/echo-admin-backup"
NGINX_CONF="/etc/nginx/sites-available/echo-admin"
NGINX_ENABLED="/etc/nginx/sites-enabled/echo-admin"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印成功信息
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 函数：打印错误信息
error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# 函数：打印警告信息
warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    error "请使用 root 用户或 sudo 运行此脚本"
fi

# 步骤 1: 备份现有部署
if [ -d "$PROJECT_DIR" ]; then
    echo ""
    echo "步骤 1: 备份现有部署..."
    BACKUP_TIME=$(date +%Y%m%d_%H%M%S)
    mkdir -p "$BACKUP_DIR"
    cp -r "$PROJECT_DIR" "$BACKUP_DIR/echo-admin-$BACKUP_TIME"
    success "备份完成: $BACKUP_DIR/echo-admin-$BACKUP_TIME"
else
    echo ""
    echo "步骤 1: 首次部署，跳过备份"
fi

# 步骤 2: 创建项目目录
echo ""
echo "步骤 2: 创建项目目录..."
mkdir -p "$PROJECT_DIR/backend"
mkdir -p "$PROJECT_DIR/frontend"
success "项目目录创建完成"

# 步骤 3: 部署后端
echo ""
echo "步骤 3: 部署后端..."
cd "$PROJECT_DIR/backend"

# 检查 Python 虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r requirements.txt
success "后端依赖安装完成"

# 初始化管理员账号
echo ""
echo "初始化管理员账号..."
python init_admin.py
success "管理员账号初始化完成"

# 步骤 4: 部署前端
echo ""
echo "步骤 4: 部署前端..."
cd "$PROJECT_DIR/frontend"

# 安装依赖
echo "安装前端依赖..."
npm install
success "前端依赖安装完成"

# 构建前端
echo "构建前端..."
npm run build
success "前端构建完成"

# 步骤 5: 配置 Nginx
echo ""
echo "步骤 5: 配置 Nginx..."
cp "$PROJECT_DIR/../deployment/nginx.conf" "$NGINX_CONF"
ln -sf "$NGINX_CONF" "$NGINX_ENABLED"
success "Nginx 配置完成"

# 测试 Nginx 配置
nginx -t || error "Nginx 配置测试失败"

# 步骤 6: 配置 Supervisor
echo ""
echo "步骤 6: 配置 Supervisor..."
cp "$PROJECT_DIR/../deployment/supervisor.conf" "/etc/supervisor/conf.d/echo-admin.conf"
success "Supervisor 配置完成"

# 重新加载 Supervisor
supervisorctl reread
supervisorctl update
success "Supervisor 配置已重新加载"

# 步骤 7: 启动服务
echo ""
echo "步骤 7: 启动服务..."

# 重启 Nginx
systemctl reload nginx
success "Nginx 已重新加载"

# 启动 echo-admin 服务
supervisorctl restart echo-admin
success "echo-admin 服务已启动"

# 步骤 8: 验证部署
echo ""
echo "步骤 8: 验证部署..."
sleep 3

# 检查服务状态
if supervisorctl status echo-admin | grep -q "RUNNING"; then
    success "echo-admin 服务运行正常"
else
    error "echo-admin 服务启动失败"
fi

# 完成
echo ""
echo "======================================"
success "部署完成！"
echo "======================================"
echo ""
echo "默认管理员账号："
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
warn "⚠ 请及时修改默认密码！"
echo ""
echo "访问地址: http://admin.echo-app.com"
echo "API 地址: http://admin.echo-app.com/api"
echo ""
echo "日志位置："
echo "  后端日志: tail -f /var/log/supervisor/echo-admin.stderr.log"
echo "  Nginx 日志: tail -f /var/log/nginx/echo-admin-error.log"
echo ""
