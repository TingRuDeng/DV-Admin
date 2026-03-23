# Quality Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前“文档要求为主”的质量要求落成仓库内可执行、可失败、可复现的强制门禁，覆盖 `frontend`、`backend`（Django）和 `fastapi`。

**Architecture:** 以仓库根目录 CI 作为唯一硬门禁；各子项目暴露稳定的一组本地检查命令；前端继续保留 Husky 作为本地便利层，但是否允许合并由 CI 决定。Django 后端补齐 `ruff + pytest` 的工程配置，FastAPI 后端保留现有测试/覆盖率能力并统一入口。

**Tech Stack:** GitHub Actions、pnpm、Vite、Vitest、Playwright、uv、pytest、pytest-django、ruff、mypy。

---

## 背景结论

- 现状不是“前端强制、后端没有”这么简单，而是：
- `frontend` 的工具链最完整，已有 `lint`、`type-check`、`vitest`、`playwright`、`husky`、`commitlint`、`lint-staged`。
- `frontend` 仍缺少仓库级 CI，且 `build` 脚本中的 `vue-tsc --noEmit & vite build` 不是严格阻塞式写法。
- `backend` 的 `pyproject.toml` 只有运行时依赖，没有把 `pytest`、`ruff`、类型检查或本地门禁真正配置进工程。
- `backend` 虽然已有测试文件和 `drf_admin/settings_test.py`，但仓库内没有 `.env.test`，默认测试环境仍不稳定。
- `fastapi` 已经配置了 `pytest`、`ruff`、`mypy`、覆盖率下限 `80`，但也没有 CI 或统一的 merge gate。
- 根目录当前没有 `.github/workflows/`，所以三个子项目都没有真正的“合并阻断”。

## 目标状态

- 任一 PR 只要破坏前端 lint、类型检查或单测，CI 立即失败。
- 任一 PR 只要破坏 Django 后端 lint 或测试，CI 立即失败。
- 任一 PR 只要破坏 FastAPI 后端 lint、类型检查、测试或覆盖率下限，CI 立即失败。
- `AGENTS.md`、`docs/README.md`、各子项目 README 中出现的检查命令都能真实执行。
- 本地开发者不依赖记忆执行检查；至少存在一套统一命令或统一入口。

## 约束与边界

- 不修改任何业务 API 契约，不改 URL、参数、响应格式。
- Phase 1 不把 Playwright E2E 设为必过门禁；它依赖完整前后端运行环境，更适合作为单独工作流或后续增强。
- Phase 1 不要求 Django 立即上严格 `mypy`；先完成 `ruff + pytest` 的稳定门禁，再评估类型系统。
- FastAPI 现有覆盖率阈值保留，避免回退。

## 建议实施顺序

- Task 1 先完成前端命令对齐，因为它会影响后续 CI 的调用方式。
- Task 2 和 Task 3 可以并行，写集互不冲突。
- Task 4 在前三项完成后再做，把三套命令接进 CI。
- Task 5 最后做文档同步和验收收口。

## 推荐委派方式

- Agent A 负责 `frontend/`
- Agent B 负责 `backend/`
- Agent C 负责 `fastapi/`
- 主执行者最后整合 `.github/workflows/quality-gates.yml` 与文档

### Task 1: Harden Frontend Quality Contract

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/README.md`
- Optional modify: `frontend/.husky/pre-commit`
- Test: `frontend/vitest.config.ts`

- [ ] **Step 1: 对齐前端“文档命令”和“真实脚本”**

目标：
- 增加 `test:unit` 别名，避免 `AGENTS.md` 中的 `pnpm run test:unit` 与现状不一致。
- 增加一个稳定聚合命令，例如 `quality` 或 `check`，供 CI 和人工统一调用。

建议结果：

```json
{
  "scripts": {
    "type-check": "vue-tsc --noEmit",
    "test:run": "vitest run",
    "test:unit": "vitest run",
    "quality": "pnpm run lint && pnpm run type-check && pnpm run test:unit"
  }
}
```

- [ ] **Step 2: 修正 `build` 的阻塞语义**

当前 `build` 使用 `vue-tsc --noEmit & vite build`，应改为严格串行或显式失败传播。

建议结果：

```json
{
  "scripts": {
    "build": "pnpm run type-check && vite build"
  }
}
```

- [ ] **Step 3: 决定 Husky 是否继续只做 staged lint**

推荐保留现状，不把全量单测塞进 pre-commit。原因：
- staged lint 反馈快；
- merge gate 由 CI 承担；
- 避免本地提交过慢造成绕过 hook 的冲动。

若保留，则只需确认 `frontend/.husky/pre-commit` 继续调用 `lint-staged` 即可。

- [ ] **Step 4: 运行前端基线验证**

Run:

```bash
cd frontend
pnpm install
pnpm run quality
pnpm run build
```

Expected:
- `quality` 通过
- `build` 遇到类型错误时能直接失败

- [ ] **Step 5: 提交前端独立改动**

```bash
git add frontend/package.json frontend/README.md frontend/.husky/pre-commit
git commit -m "build(frontend): harden quality gate commands"
```

### Task 2: Add First-Class Django Backend Quality Tooling

**Files:**
- Modify: `backend/pyproject.toml`
- Create: `backend/pytest.ini`
- Create: `backend/conftest.py`
- Create: `backend/.env.test`
- Optional modify: `backend/README.md`
- Test: `backend/drf_admin/apps/oauth/tests.py`
- Test: `backend/drf_admin/apps/system/test_roles.py`

- [ ] **Step 1: 为 Django 后端补齐 dev tooling 依赖**

目标：
- 在 `backend/pyproject.toml` 中引入 `pytest`、`pytest-django`、`ruff`。
- 如果需要测试数据库辅助工具，再按最小集补依赖，不要一次性上 `mypy`、`black`、`isort` 全家桶。

建议最小集：

```toml
[dependency-groups]
dev = [
  "pytest>=8.0.0",
  "pytest-django>=4.8.0",
  "ruff>=0.6.0",
]
```

- [ ] **Step 2: 固化 Django pytest 入口**

创建 `backend/pytest.ini`，显式绑定测试设置：

```ini
[pytest]
DJANGO_SETTINGS_MODULE = drf_admin.settings_test
python_files = tests.py test_*.py *_tests.py
testpaths = drf_admin/apps
addopts = -v --tb=short --strict-markers
```

创建 `backend/conftest.py`，最少保证：

```python
import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_admin.settings_test")
```

- [ ] **Step 3: 消除 `.env.test` 缺失导致的不确定性**

`drf_admin.settings_test` 仍会 import `drf_admin.settings`，而后者要求存在 `.env.test`。本任务必须让测试环境自举成功。

推荐方案：
- 直接提交一个安全的 `backend/.env.test`，只用于测试；
- 使用 SQLite、假的 `SECRET_KEY`、本地 `ALLOWED_HOSTS`、空 Redis。

最低内容示例：

```env
SECRET_KEY=test-secret-key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost,testserver
DATABASE_URL=sqlite:///./test.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:9527,http://127.0.0.1:9527
EXTRA_INSTALLED_APPS=
```

- [ ] **Step 4: 添加 Ruff 配置并跑通最小基线**

优先把配置放在 `backend/pyproject.toml`，避免多文件分散。

建议最小规则集：

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]
```

先以低风险规则集落地，后续再逐步扩展。

- [ ] **Step 5: 运行 Django 后端验证**

Run:

```bash
cd backend
uv sync --group dev
uv run ruff check .
uv run pytest
```

Expected:
- `ruff check` 可稳定运行
- pytest 能在仓库默认状态下直接启动，不依赖手工补环境文件

- [ ] **Step 6: 提交 Django 后端独立改动**

```bash
git add backend/pyproject.toml backend/pytest.ini backend/conftest.py backend/.env.test backend/README.md
git commit -m "build(backend): add django quality gate tooling"
```

### Task 3: Normalize FastAPI Quality Entry Points

**Files:**
- Modify: `fastapi/pyproject.toml`
- Create: `fastapi/Makefile`
- Optional modify: `fastapi/README.md`
- Optional modify: `fastapi/TESTING.md`
- Test: `fastapi/tests/conftest.py`

- [ ] **Step 1: 统一 FastAPI 本地执行入口**

FastAPI 已有规则，但缺少一眼可见的统一命令。建议增加 `fastapi/Makefile`：

```makefile
lint:
	uv run ruff check .

typecheck:
	uv run mypy app

test:
	uv run pytest --cov=app --cov-report=term-missing

quality:
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test
```

- [ ] **Step 2: 清理 `pyproject.toml` 中重复或分裂的 dev 配置**

目标：
- 确定最终只使用一种 dev 依赖组织方式；
- 保留现有 `pytest`、`ruff`、`mypy`、coverage 阈值；
- 避免同时维护 `[project.optional-dependencies].dev` 和 `[dependency-groups].dev` 两套来源。

推荐：
- 统一到 `[dependency-groups].dev`
- 删除重复项或在文档中明确哪套为权威

- [ ] **Step 3: 跑通 FastAPI 质量基线**

Run:

```bash
cd fastapi
uv sync --group dev
make quality
```

Expected:
- `ruff`、`mypy`、`pytest --cov` 均可跑通
- 覆盖率仍维持 `fail_under = 80`

- [ ] **Step 4: 提交 FastAPI 独立改动**

```bash
git add fastapi/pyproject.toml fastapi/Makefile fastapi/README.md fastapi/TESTING.md
git commit -m "build(fastapi): normalize quality entry points"
```

### Task 4: Add Root-Level Hard Gate CI

**Files:**
- Create: `.github/workflows/quality-gates.yml`

- [ ] **Step 1: 创建仓库级 workflow**

触发条件建议：

```yaml
on:
  pull_request:
  push:
    branches:
      - main
```

- [ ] **Step 2: 添加前端 job**

建议命令：

```yaml
- working-directory: frontend
  run: pnpm install --frozen-lockfile
- working-directory: frontend
  run: pnpm run quality
- working-directory: frontend
  run: pnpm run build
```

- [ ] **Step 3: 添加 Django job**

建议命令：

```yaml
- working-directory: backend
  run: uv sync --group dev
- working-directory: backend
  run: uv run ruff check .
- working-directory: backend
  run: uv run pytest
```

注意：
- 若 `.env.test` 不提交到仓库，则在 workflow 中先执行 `cp .env.example .env.test` 并覆写必要测试变量。
- 若提交 `backend/.env.test`，则 CI 只需直接运行测试。

- [ ] **Step 4: 添加 FastAPI job**

建议命令：

```yaml
- working-directory: fastapi
  run: uv sync --group dev
- working-directory: fastapi
  run: make quality
```

- [ ] **Step 5: 将 E2E 排除在默认 required checks 之外**

本阶段不把 `frontend` 的 Playwright 纳入必过门禁，除非同时交付：
- 稳定的测试环境编排；
- 可复现的前后端启动脚本；
- CI 中可控的 fixture 数据准备。

- [ ] **Step 6: 提交 CI 独立改动**

```bash
git add .github/workflows/quality-gates.yml
git commit -m "ci: add repository quality gates"
```

### Task 5: Sync Docs and Acceptance Contract

**Files:**
- Modify: `AGENTS.md`
- Modify: `docs/README.md`
- Modify: `docs/DOC_SYNC_CHECKLIST.md`
- Optional modify: `frontend/README.md`
- Optional modify: `backend/README.md`
- Optional modify: `fastapi/README.md`

- [ ] **Step 1: 对齐文档中的命令名称**

必须修正以下偏差：
- `AGENTS.md` 中的 `pnpm run test:unit` 必须与前端脚本一致
- `AGENTS.md` 中的后端 `ruff check` 必须与实际可运行配置一致
- `docs/DOC_SYNC_CHECKLIST.md` 中的检查项必须对应真实命令

- [ ] **Step 2: 在文档中明确“强制门禁”的定义**

建议增加一句明确表述：
- “本仓库以 `.github/workflows/quality-gates.yml` 为合并前强制门禁。”

- [ ] **Step 3: 做最终验收**

验收命令：

```bash
cd frontend && pnpm run quality && pnpm run build
cd backend && uv run ruff check . && uv run pytest
cd fastapi && make quality
```

最终人工验收项：
- 制造一个前端 lint 错误，确认 CI 失败
- 制造一个 Django 测试失败，确认 CI 失败
- 制造一个 FastAPI 覆盖率下降或类型错误，确认 CI 失败

- [ ] **Step 4: 提交文档同步改动**

```bash
git add AGENTS.md docs/README.md docs/DOC_SYNC_CHECKLIST.md frontend/README.md backend/README.md fastapi/README.md
git commit -m "docs: sync quality gate contract"
```

## 验收标准

- 存在根目录 `.github/workflows/quality-gates.yml`
- 前端存在单一聚合命令，且 `build` 对类型错误敏感
- Django 后端可在仓库默认状态下执行 `uv run ruff check .` 与 `uv run pytest`
- FastAPI 后端可在仓库默认状态下执行 `make quality`
- 文档中的检查命令与工程脚本一一对应

## 非目标

- 不在本轮引入 SonarQube、Codecov、Danger、Reviewdog 等额外平台
- 不在本轮把所有历史 Django 警告一次性清零
- 不在本轮设计夜间 E2E、基准测试、性能回归门禁

## 风险提示

- Django 历史代码可能一次性触发大量 `ruff` 问题，必要时先用最小规则集落地，再逐步加严。
- 若 `backend/.env.test` 包含任何非测试用途配置，不应提交；此文件只能承载测试安全值。
- FastAPI 的 `mypy` 可能暴露现有隐患，若失败数量过大，可先限定检查范围到 `app/api`、`app/services` 等核心路径，但不得静默移除类型门禁。

## 交付建议

- 首轮实施采用 4 个独立 PR 更稳妥：
- PR 1: `frontend` 质量命令对齐
- PR 2: `backend` Django 质量工具链补齐
- PR 3: `fastapi` 质量入口统一
- PR 4: 根目录 CI 与文档同步

- 若需要单 PR，也必须按上述顺序提交中间 commit，避免一次性大改难以回滚。
