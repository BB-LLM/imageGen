#!/bin/bash

################################################################################
# imageGen 停止脚本
# 功能: 停止 imageGen 服务（杀掉端口 8000 的所有进程）
# 用法: ./stop.sh
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
API_PORT=8000

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  停止 imageGen 服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 查找占用端口的进程
echo -e "${YELLOW}🔍 查找占用端口 $API_PORT 的进程...${NC}"

# 使用多种方法查找进程，确保能找到
PIDS=""

# 方法1: 使用 lsof (如果可用)
if command -v lsof &> /dev/null; then
    PIDS=$(lsof -ti :$API_PORT 2>/dev/null || true)
fi

# 方法2: 如果 lsof 没找到，使用 netstat
if [ -z "$PIDS" ] && command -v netstat &> /dev/null; then
    PIDS=$(netstat -tlnp 2>/dev/null | grep ":$API_PORT " | awk '{print $7}' | cut -d'/' -f1 | grep -E '^[0-9]+$' || true)
fi

# 方法3: 如果还是没找到，使用 ss
if [ -z "$PIDS" ] && command -v ss &> /dev/null; then
    PIDS=$(ss -tlnp 2>/dev/null | grep ":$API_PORT " | grep -oP 'pid=\K[0-9]+' || true)
fi

# 方法4: 如果还是没找到，直接查找 uvicorn 进程
if [ -z "$PIDS" ]; then
    PIDS=$(ps aux | grep -E "[u]vicorn.*:$API_PORT|[p]ython.*main.py" | awk '{print $2}' || true)
fi

if [ -z "$PIDS" ]; then
    echo -e "${GREEN}✅ 端口 $API_PORT 没有被占用${NC}"
    exit 0
fi

# 显示找到的进程
echo -e "${YELLOW}找到以下进程:${NC}"
for PID in $PIDS; do
    PROCESS_INFO=$(ps -p $PID -o pid,cmd --no-headers 2>/dev/null || echo "$PID (进程已结束)")
    echo -e "  ${YELLOW}PID: $PROCESS_INFO${NC}"
done
echo ""

# 杀掉进程
echo -e "${YELLOW}🔪 正在停止进程...${NC}"
for PID in $PIDS; do
    # 先尝试优雅关闭 (SIGTERM)
    if kill $PID 2>/dev/null; then
        echo -e "${YELLOW}⏳ 发送 SIGTERM 信号到进程 $PID...${NC}"
        sleep 1

        # 检查进程是否还在运行
        if ps -p $PID > /dev/null 2>&1; then
            # 如果还在运行，强制杀掉 (SIGKILL)
            echo -e "${YELLOW}⚠️  进程 $PID 未响应，使用 SIGKILL 强制停止...${NC}"
            if kill -9 $PID 2>/dev/null; then
                echo -e "${GREEN}✅ 已强制停止进程 $PID${NC}"
            else
                echo -e "${RED}⚠️  无法停止进程 $PID (可能需要 root 权限)${NC}"
            fi
        else
            echo -e "${GREEN}✅ 已停止进程 $PID${NC}"
        fi
    else
        echo -e "${RED}⚠️  无法停止进程 $PID (可能已结束或需要 root 权限)${NC}"
    fi
done

# 等待进程完全结束
sleep 1

# 再次检查
echo ""
echo -e "${YELLOW}🔍 验证端口是否已释放...${NC}"
REMAINING=""

if command -v lsof &> /dev/null; then
    REMAINING=$(lsof -ti :$API_PORT 2>/dev/null || true)
fi

if [ -z "$REMAINING" ] && command -v netstat &> /dev/null; then
    REMAINING=$(netstat -tlnp 2>/dev/null | grep ":$API_PORT " | awk '{print $7}' | cut -d'/' -f1 | grep -E '^[0-9]+$' || true)
fi

if [ -z "$REMAINING" ] && command -v ss &> /dev/null; then
    REMAINING=$(ss -tlnp 2>/dev/null | grep ":$API_PORT " | grep -oP 'pid=\K[0-9]+' || true)
fi

if [ -z "$REMAINING" ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  imageGen 服务已成功停止${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  警告: 仍有进程占用端口 $API_PORT${NC}"
    echo -e "${RED}  进程 PID: $REMAINING${NC}"
    echo -e "${RED}  请尝试: sudo kill -9 $REMAINING${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi

