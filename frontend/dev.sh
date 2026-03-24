#!/bin/bash
# 前端开发环境启动脚本
# 使用说明：chmod +x dev.sh && ./dev.sh [start|stop|status]

##############################################################################
# 配置变量
##############################################################################
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PID_FILE="${PROJECT_DIR}/dev.pid"
LOG_DIR="${PROJECT_DIR}/../logs/frontend"
DEFAULT_PORT=9527

##############################################################################

check_pnpm() {
    if ! command -v pnpm &> /dev/null; then
        echo "❌ 未检测到 pnpm 工具"
        echo "   安装：npm install -g pnpm"
        exit 1
    fi
}

start() {
    check_pnpm

    local port="$DEFAULT_PORT"
    while [[ $# -gt 0 ]]; do
        case $1 in
            --port=*)
                port="${1#*=}"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    # 检查 PID
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "✅ 前端已运行（PID: $pid）"
            return 0
        fi
    fi

    # 创建日志目录
    [ -d "$LOG_DIR" ] || mkdir -p "$LOG_DIR"

    # 安装依赖
    echo "检查依赖..."
    pnpm install

    # 启动
    cd "$PROJECT_DIR" || exit 1
    pnpm run dev --host 0.0.0.0 --port $port >> "$LOG_DIR/dev.log" 2>&1 &
    local server_pid=$!
    echo $server_pid > "$PID_FILE"

    sleep 3
    if ps -p "$server_pid" > /dev/null 2>&1; then
        echo "✅ 前端启动成功（PID: $server_pid）"
        echo "   地址：http://localhost:$port/"
        echo "   日志：$LOG_DIR/dev.log"
    else
        rm -f "$PID_FILE"
        echo "❌ 启动失败"
        exit 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ 前端未运行"
        return 1
    fi

    local pid=$(cat "$PID_FILE")
    if ! ps -p "$pid" > /dev/null 2>&1; then
        rm -f "$PID_FILE"
        echo "✅ 前端未运行"
        return 0
    fi

    kill "$pid" 2>/dev/null
    sleep 1
    ps -p "$pid" > /dev/null 2>&1 && kill -9 "$pid" 2>/dev/null
    rm -f "$PID_FILE"
    echo "✅ 前端已停止"
}

status() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ 前端未运行"
        return 1
    fi

    local pid=$(cat "$PID_FILE")
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "✅ 前端运行中（PID: $pid）"
    else
        rm -f "$PID_FILE"
        echo "❌ 前端未运行"
    fi
}

##############################################################################

case "$1" in
    start)
        shift
        start "$@"
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    *)
        echo "前端开发脚本"
        echo ""
        echo "用法："
        echo "  ./dev.sh start           # 启动"
        echo "  ./dev.sh start --port=9528  # 指定端口"
        echo "  ./dev.sh stop            # 停止"
        echo "  ./dev.sh status          # 状态"
        exit 1
        ;;
esac
