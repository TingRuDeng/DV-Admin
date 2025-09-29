#!/bin/bash
# 测试环境 Gunicorn 启停脚本（适配 uv 依赖管理工具）
# 使用说明：chmod +x service.sh && ./service.sh [start|stop|restart|status]

##############################################################################
# 请根据你的测试环境修改以下变量（核心配置）
##############################################################################
# 1. 项目根目录（manage.py 所在目录）
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

# 2. 检查项目根目录下是否存在 manage.py（确保脚本放在正确位置）
if [ ! -f "${PROJECT_DIR}/manage.py" ]; then
    echo "❌ 脚本位置错误！未在项目根目录找到 manage.py"
    echo "   请将脚本放在 Django 项目根目录（与 manage.py 同级）后重试"
    exit 1
fi

# 2. uv 创建的虚拟环境路径（uv venv 生成的目录，默认 .venv）
VENV_DIR="${PROJECT_DIR}/.venv"  # uv 推荐的虚拟环境目录
# 3. Gunicorn 配置文件路径（可选，无则留空）
#GUNICORN_CONFIG="${PROJECT_DIR}/gunicorn_config.py"
# 4. PID 文件路径
PID_FILE="${PROJECT_DIR}/gunicorn.pid"
# 5. 日志目录
LOG_DIR="${PROJECT_DIR}/logs/gunicorn"
# 7. 绑定地址
BIND_ADDR="127.0.0.1:8769"
# 8. 工作进程数（测试环境 2-4 个足够）
WORKERS=4

##############################################################################
# 脚本核心函数
##############################################################################

# 检查 uv 是否安装
check_uv() {
    if ! command -v uv &> /dev/null; then
        echo "❌ 未检测到 uv 工具，请参考以下说明安装"
        echo "   执行命令：curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "   安装完成后，执行：source ~/.bashrc"
        exit 1
    fi
}

# 启动 Gunicorn
start() {
    # 检查 uv 安装
    check_uv

    # 检查项目目录
    if [ ! -d "${PROJECT_DIR}" ]; then
        echo "❌ 项目目录不存在：${PROJECT_DIR}"
        exit 1
    else
        cd "${PROJECT_DIR}" || {
            echo "❌ 切换到项目目录失败：${PROJECT_DIR}"
            exit 1
        }
    fi

    # 执行 uv sync 更新依赖（无论虚拟环境是否存在）
    echo "ℹ️  正在同步项目环境及依赖..."
    uv sync
    if [ $? -ne 0 ]; then
        echo "❌ uv sync 执行失败，无法更新依赖"
        exit 1
    fi
    echo "✅ 依赖更新成功"

    # 检查 PID 文件（避免重复启动）
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat "${PID_FILE}")
        if ps -p "${PID}" > /dev/null 2>&1; then
            echo "✅ drf_admin 已在运行（PID: ${PID}）"
            exit 0
        else
            echo "⚠️  清理残留 PID 文件"
            rm -f "${PID_FILE}"
        fi
    fi

    # 创建日志目录
    if [ ! -d "${LOG_DIR}" ]; then
        mkdir -p "${LOG_DIR}"
        echo "ℹ️  已创建日志目录：${LOG_DIR}"
    fi

    # 启动命令（兼容配置文件和命令行参数）
    if [ -f "${GUNICORN_CONFIG}" ]; then
        uv run gunicorn \
            --daemon \
            --config "${GUNICORN_CONFIG}" \
            --pid "${PID_FILE}" \
            --bind "${BIND_ADDR}" \
            --workers "${WORKERS}" \
            --access-logfile "${LOG_DIR}/access.log" \
            --error-logfile "${LOG_DIR}/error.log" \
            "drf_admin.wsgi:application"
    else
        uv run gunicorn \
            --daemon \
            --pid "${PID_FILE}" \
            --bind "${BIND_ADDR}" \
            --workers "${WORKERS}" \
            --access-logfile "${LOG_DIR}/access.log" \
            --error-logfile "${LOG_DIR}/error.log" \
            "drf_admin.wsgi:application"
    fi

    # 检查启动结果
    sleep 2
    if [ -f "${PID_FILE}" ] && ps -p "$(cat "${PID_FILE}")" > /dev/null 2>&1; then
        echo "✅ drf_admin 启动成功（PID: $(cat "${PID_FILE}")，绑定: ${BIND_ADDR}）"
    else
        echo "❌ 启动失败，查看日志：${LOG_DIR}/error.log"
        exit 1
    fi
}

# 停止 Gunicorn
stop() {
    if [ ! -f "${PID_FILE}" ]; then
        echo "❌ PID 文件不存在，drf_admin 未运行"
        return 1
    fi

    PID=$(cat "${PID_FILE}")
    if ! ps -p "${PID}" > /dev/null 2>&1; then
        echo "⚠️  清理残留 PID 文件"
        rm -f "${PID_FILE}"
        return 0
    fi

    echo "ℹ️  正在停止 drf_admin（PID: ${PID}）..."
    kill "${PID}" || {
        echo "⚠️  强制终止进程..."
        kill -9 "${PID}"
    }

    sleep 2
    if ! ps -p "${PID}" > /dev/null 2>&1; then
        rm -f "${PID_FILE}"
        echo "✅ drf_admin 已停止"
        return 0
    else
        echo "❌ 停止失败，请手动终止 PID: ${PID}"
        return 1
    fi
}

# 重启 Gunicorn
restart() {
    echo "ℹ️  正在重启 drf_admin..."
    stop || true
    start
}

# 查看状态
status() {
    if [ ! -f "${PID_FILE}" ]; then
        echo "❌ drf_admin 未运行"
        exit 1
    fi

    PID=$(cat "${PID_FILE}")
    if ps -p "${PID}" > /dev/null 2>&1; then
        echo "✅ drf_admin 运行中（uv 环境）"
        echo "   - PID: ${PID}"
        echo "   - 绑定: ${BIND_ADDR}"
        echo "   - 虚拟环境: ${VENV_DIR}"
    else
        echo "❌ drf_admin 已停止，清理残留 PID 文件"
        rm -f "${PID_FILE}"
    fi
}

##############################################################################
# 脚本入口
##############################################################################
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "❌ 无效参数，使用："
        echo "   ./service.sh [start|stop|restart|status]"
        exit 1
        ;;
esac
