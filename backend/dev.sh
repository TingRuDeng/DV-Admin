#!/bin/bash
# Django 开发环境启动脚本
# 使用说明：chmod +x dev.sh && ./dev.sh [start|stop|restart|status|logs]

##############################################################################
# 配置变量
##############################################################################
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LOG_DIR="${PROJECT_DIR}/logs/dev"
PID_FILE="${LOG_DIR}/dev.pid"
DEFAULT_ENV_FILE="${PROJECT_DIR}/.env.dev"

##############################################################################

check_uv() {
    if ! command -v uv &> /dev/null; then
        echo "❌ 未检测到 uv 工具"
        echo "   安装：curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
}

check_dependencies() {
    echo "检查依赖..."
    if [ ! -d ".venv" ]; then
        echo "虚拟环境不存在，正在创建..."
        uv venv
    fi
    echo "同步依赖..."
    uv sync
    echo "✅ 依赖已就绪"
}

check_env_file() {
    local env_file="$1"
    if [ -z "$env_file" ]; then
        env_file="$DEFAULT_ENV_FILE"
    fi

    if [ ! -f "$env_file" ]; then
        echo "❌ 配置文件不存在：$env_file"
        echo ""
        echo "请创建配置文件："
        echo "   cp .env.example $env_file"
        exit 1
    fi
    echo "✅ 使用配置文件：$env_file"
}

start() {
    check_uv
    check_dependencies

    local env_name="dev"
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env=*)
                env_name="${1#*=}"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    local env_file="${PROJECT_DIR}/.env.${env_name}"
    check_env_file "$env_file"

    # 检查 PID
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "✅ Django 已运行（PID: $pid）"
            return 0
        fi
    fi

    # 创建日志目录
    [ -d "$LOG_DIR" ] || mkdir -p "$LOG_DIR"

    # 启动
    cd "$PROJECT_DIR" || exit 1
    uv run python manage.py runserver 0.0.0.0:8769 --env "$env_name" >> "$LOG_DIR/dev.log" 2>&1 &
    local server_pid=$!
    echo $server_pid > "$PID_FILE"

    sleep 2
    if ps -p "$server_pid" > /dev/null 2>&1; then
        echo "✅ Django 启动成功（PID: $server_pid）"
        echo "   日志：$LOG_DIR/dev.log"
    else
        rm -f "$PID_FILE"
        echo "❌ 启动失败"
        exit 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Django 未运行"
        return 1
    fi

    local pid=$(cat "$PID_FILE")
    if ! ps -p "$pid" > /dev/null 2>&1; then
        rm -f "$PID_FILE"
        echo "✅ Django 未运行"
        return 0
    fi

    kill "$pid" 2>/dev/null
    sleep 1
    ps -p "$pid" > /dev/null 2>&1 && kill -9 "$pid" 2>/dev/null
    rm -f "$PID_FILE"
    echo "✅ Django 已停止"
}

restart() {
    stop
    sleep 1
    start "$@"
}

status() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Django 未运行"
        return 1
    fi

    local pid=$(cat "$PID_FILE")
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "✅ Django 运行中（PID: $pid）"
        echo "   日志：$LOG_DIR/dev.log"
    else
        rm -f "$PID_FILE"
        echo "❌ Django 未运行"
    fi
}

logs() {
    if [ -f "$LOG_DIR/dev.log" ]; then
        tail -f "$LOG_DIR/dev.log"
    else
        echo "❌ 日志文件不存在"
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
    restart)
        shift
        restart "$@"
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "Django 开发脚本"
        echo ""
        echo "用法："
        echo "  ./dev.sh start              # 启动"
        echo "  ./dev.sh start --env=test   # 指定环境启动"
        echo "  ./dev.sh stop               # 停止"
        echo "  ./dev.sh restart           # 重启"
        echo "  ./dev.sh status            # 状态"
        echo "  ./dev.sh logs              # 查看日志"
        exit 1
        ;;
esac
