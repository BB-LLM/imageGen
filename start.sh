#!/bin/bash

################################################################################
# imageGen 一键启动脚本
# 功能: 启动 imageGen 服务，所有输出写入日志文件
# 用法: ./start_imagegen.sh
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="/home/hongxda/imageGen"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/imagegen_$(date +%Y%m%d_%H%M%S).log"
VENV_DIR="${PROJECT_DIR}/venv"
API_PORT=8000

# 创建日志目录
mkdir -p "$LOG_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  imageGen 服务启动${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ 错误: 项目目录不存在: $PROJECT_DIR${NC}"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ 错误: 虚拟环境不存在: $VENV_DIR${NC}"
    echo -e "${YELLOW}请先创建虚拟环境:${NC}"
    echo -e "  cd $PROJECT_DIR"
    echo -e "  python3.10 -m venv venv"
    exit 1
fi

echo -e "${YELLOW}📁 项目目录: $PROJECT_DIR${NC}"
echo -e "${YELLOW}🐍 虚拟环境: $VENV_DIR${NC}"
echo -e "${YELLOW}📝 日志文件: $LOG_FILE${NC}"
echo ""

# 进入项目目录
cd "$PROJECT_DIR"

# 检查并清理端口 8000
echo -e "${YELLOW}🔍 检查端口 $API_PORT 是否被占用...${NC}"
EXISTING_PIDS=$(lsof -ti :$API_PORT 2>/dev/null || true)

if [ -n "$EXISTING_PIDS" ]; then
    echo -e "${YELLOW}⚠️  发现端口 $API_PORT 已被占用，正在清理旧进程...${NC}"
    for PID in $EXISTING_PIDS; do
        PROCESS_INFO=$(ps -p $PID -o cmd --no-headers 2>/dev/null || echo "未知进程")
        echo -e "${YELLOW}  停止进程 $PID: $PROCESS_INFO${NC}"
        kill -9 $PID 2>/dev/null || true
    done
    sleep 1
    echo -e "${GREEN}✅ 旧进程已清理${NC}"
else
    echo -e "${GREEN}✅ 端口 $API_PORT 可用${NC}"
fi
echo ""

# 启动服务（后台运行，输出到日志）
echo -e "${YELLOW}🚀 启动 imageGen 服务...${NC}"
echo "启动时间: $(date)" > "$LOG_FILE"
echo "虚拟环境: $VENV_DIR" >> "$LOG_FILE"
echo "项目目录: $PROJECT_DIR" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 激活本地虚拟环境
source "$VENV_DIR/bin/activate" 2>/dev/null || {
    echo -e "${RED}❌ 错误: 无法激活虚拟环境 '$VENV_DIR'${NC}"
    exit 1
}

# 设置环境变量，禁用 DEBUG 模式
export DEBUG=False
export PUBLIC_API_URL="http://34.148.94.241:8000"
# 启动服务（后台运行，使用 setsid + nohup 确保进程完全从终端分离）
setsid nohup python main.py >> "$LOG_FILE" 2>&1 &
SERVICE_PID=$!

# 等待服务启动
sleep 2

# 检查进程是否还在运行
if ! kill -0 $SERVICE_PID 2>/dev/null; then
    echo -e "${RED}❌ 服务启动失败！${NC}"
    echo -e "${RED}请查看日志: $LOG_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ imageGen 服务已启动${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  服务信息${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}进程号 (PID): $SERVICE_PID${NC}"
echo -e "${GREEN}服务地址: http://34.148.94.241:8000${NC}"
echo -e "${GREEN}API 文档: http://34.148.94.241:8000/docs${NC}"
echo -e "${GREEN}日志文件: $LOG_FILE${NC}"
echo ""
echo -e "${YELLOW}💡 提示:${NC}"
echo -e "  - 查看实时日志: tail -f $LOG_FILE"
echo -e "  - 停止服务: kill $SERVICE_PID"
echo -e "  - 查看进程: ps aux | grep $SERVICE_PID"
echo ""

# 输出进程号到文件（便于后续管理）
echo "$SERVICE_PID" > "${LOG_DIR}/imagegen.pid"

echo -e "${GREEN}✨ 启动完成！${NC}"

