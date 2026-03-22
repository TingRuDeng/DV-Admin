#!/bin/bash

# DV-Admin FastAPI 开发环境启动脚本
# 使用方法: ./scripts/dev.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DV-Admin FastAPI 开发环境启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv 未安装，正在安装...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}虚拟环境不存在，正在创建...${NC}"
    uv venv
fi

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}.env 文件不存在，正在从 .env.example 复制...${NC}"
    cp .env.example .env
fi

# 创建上传目录
if [ ! -d "uploads" ]; then
    echo -e "${YELLOW}创建上传目录...${NC}"
    mkdir -p uploads/avatar uploads/files
fi

# 同步依赖
echo -e "${GREEN}同步依赖...${NC}"
uv sync

# 启动服务
echo ""
echo -e "${GREEN}启动 FastAPI 开发服务器...${NC}"
echo -e "${BLUE}服务地址: http://localhost:8769${NC}"
echo -e "${BLUE}API 文档: http://localhost:8769/api/swagger/${NC}"
echo -e "${BLUE}ReDoc: http://localhost:8769/api/redoc/${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8769
