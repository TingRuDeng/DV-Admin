.PHONY: lint typecheck test quality format clean help

help:
	@echo "FastAPI 质量检查命令:"
	@echo "  make lint       - 运行 ruff 代码检查"
	@echo "  make typecheck  - 运行 mypy 类型检查"
	@echo "  make test       - 运行测试并生成覆盖率报告"
	@echo "  make quality    - 运行所有质量检查 (lint + typecheck + test)"
	@echo "  make format     - 格式化代码 (black + isort)"
	@echo "  make clean      - 清理缓存和临时文件"

lint:
	uv run ruff check .

typecheck:
	uv run mypy app/schemas

test:
	uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=80

quality:
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test

format:
	uv run black .
	uv run isort .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml 2>/dev/null || true
