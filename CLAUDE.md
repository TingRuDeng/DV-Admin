# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**语言约定：所有回复一律使用中文。**

`AGENTS.md` is the repository's single authoritative rules entry (branching, quality gates, doc sync) and is enforced by `scripts/validate_docs.py`. Read it before any change; this file summarizes it and adds cross-cutting facts that take several files to discover. Project docs are in Chinese; `docs/README.md` is the navigation entry and `docs/AI_CONTEXT.md` is the short task-routing map.

## Repository shape

DV-Admin is an RBAC admin platform: one Vue 3 frontend plus **two alternative backend implementations** of the same API.

- `frontend/`: Vue 3 + TypeScript + Element Plus + Vite 8 + Pinia + Vue Router 5 (dev server on port 9527, proxies `/dev-api` to `127.0.0.1:8769`).
- `backend/`: Django 4 + DRF + simplejwt + Channels (Python ≥3.11, package `drf_admin`).
- `fastapi/`: FastAPI + Tortoise ORM, async (Python ≥3.10; CI runs 3.10, so don't use 3.11+ syntax).

Django and FastAPI are **not** upstream/downstream services. Both listen on 8769, and you run only one at a time. Any change to a shared API contract (path, method, params, response fields, pagination, error codes) must be made in **both** backends and checked against the callers in `frontend/src/api/`.

Never commit directly on `master`/`main`; work on a branch or worktree. Commits follow Conventional Commits (`frontend/commitlint.config.cjs`).

## Commands

### Frontend (`cd frontend`; Node ≥24, pnpm pinned via `packageManager`)

```bash
pnpm install --frozen-lockfile
pnpm run dev                     # or ./dev.sh start
pnpm run quality                 # lint:check + vue-tsc type-check + vitest (read-only)
pnpm run lint                    # auto-fix eslint + prettier + stylelint
pnpm run build                   # type-check + vite build
pnpm run audit:prod              # prod dependency audit (high/critical + expiring exemptions)
pnpm exec vitest run src/utils/__tests__/route-meta.test.ts     # single unit test file
pnpm run test:e2e:smoke          # Playwright smoke; starts its own Vite, API mocked via page.route
pnpm exec playwright test e2e/shell-layout.spec.ts --workers=1  # single E2E spec
VITE_APP_PORT=19527 pnpm run test:e2e:smoke                     # if 9527 is occupied
```

Playwright takes its port from `frontend/.env.development`; don't hardcode ports.

### Django (`cd backend`)

```bash
uv sync --group dev
cp .env.example .env.dev
uv run python manage.py migrate --env dev
uv run python manage.py loaddata init_data.json --env dev    # seed: admin/123456, visitor/123456
./dev.sh start                   # runserver 0.0.0.0:8769 in background; logs in logs/dev/dev.log
uv run ruff check .
uv run pytest                                                   # all tests
uv run pytest drf_admin/apps/system/test_roles.py::RolesListTestCase::test_get_roles_list   # single test
uv run python manage.py makemigrations --env dev
```

`manage.py` consumes `--env <name>` and loads `backend/.env.<name>` (default `dev`). pytest uses `drf_admin.settings_test` (in-memory SQLite, MD5 hasher, `DEFAULT_PERMISSION_CLASSES = AllowAny`) together with the tracked `backend/.env.test`.

### FastAPI (`cd fastapi`)

```bash
uv sync --group dev
cp .env.example .env             # CI appends SECRET_KEY=... and APP_ENV=test
./scripts/dev.sh                 # uvicorn app.main:app --reload --port 8769 --no-proxy-headers
make quality                     # lint (ruff --ignore I + isort check) + mypy app + migration-check + pytest (cov ≥80%)
make format                      # black + isort (line length 100)
uv run pytest tests/test_oauth.py::TestOAuthLogin::test_login_success -v   # single test (not via make; the coverage floor would fail)
uv run python -m tortoise -c app.db.migration_config.TORTOISE_ORM makemigrations models
make migration-check             # SQLite fresh / incremental / baseline takeover / model drift
```

### Repo-root validators (the "Validate docs" CI step; run from the repo root)

```bash
python3 scripts/validate_docs.py . --profile generic
python3 scripts/validate_api_contracts.py .
python3 scripts/validate_model_contracts.py .
python3 scripts/validate_route_components.py .
python3 scripts/validate_django_migrations.py .
python3 -m unittest discover -s tests -p "test_*.py"
```

### Heavy gates (CI; need extra infrastructure)

- Real-backend browser smoke with no API mocks, one run per backend. Run them sequentially, because both write to the same report dirs:
  - `(cd backend && RUN_REAL_BACKEND_PLAYWRIGHT=1 .venv/bin/pytest drf_admin/utils/runtime_api_contracts/test_live_http_contract.py::DjangoLiveHttpContractTestCase::test_shared_frontend_flow_over_real_django_http)`
  - `(cd fastapi && RUN_REAL_BACKEND_PLAYWRIGHT=1 .venv/bin/pytest tests/test_live_http_contract.py::test_shared_frontend_flow_over_real_fastapi_http)`
- `python3 scripts/verify_production_images.py --backend backend|fastapi` needs Docker.
- `scripts/verify_mysql_grants.py --backend django|fastapi` needs a MySQL 8 instance.

## Redis is required, including for tests

Login throttling needs Redis in **every** environment. There is no in-memory fallback; without Redis, login returns HTTP 503, so start Redis before local dev login. Both test suites start their own throwaway Redis through `scripts/redis_test_server.py`, so the `redis-server` binary must be on `PATH` for `pytest` to run at all. Non-security caches may fall back to memory. FastAPI production token revocation may not.

## Cross-backend architecture

**Response envelope.** Django returns `{code, msg, errors, data}`; FastAPI returns `{code, message, data}`. Success is `code == 20000`, and `40001` means the access token is invalid, which triggers one refresh and one retry in the frontend (`frontend/src/enums/api/code-enum.ts`, `frontend/src/utils/request.ts`). Pagination is `list/total` in responses and `pageNum/pageSize` in requests on both backends.

**Naming.** Python code uses snake_case and the frontend uses camelCase. Django converts automatically (the `CamelCaseMiddleWare` middleware plus camel-case parsers and renderers), so never convert by hand. Django middleware order matters (CORS → RequestId → IP blacklist → OperationLog → Response → CamelCase), and `X-Request-ID` ties responses to `OperationLog.request_id`.

**Executable contract catalog in `scripts/`.** It is checked statically from the root and at runtime in each backend:
- `api_contracts.py` holds the envelope and pagination assertions. `api_endpoint_contracts.py` plus the per-domain `api_endpoint_*_contracts.py` lock method, path, permission and key fields of critical endpoints. `api_field_contracts.py` / `api_frontend_field_contracts.py` lock response field sets on the backend and frontend sides.
- `api_runtime_route_contracts.py` registers **every** business route. `backend/drf_admin/utils/test_runtime_route_inventory.py` and `fastapi/tests/test_runtime_route_inventory.py` enumerate the real routers and fail on routes that are unregistered, removed or have drifted methods. When you add, remove or change a route, update this registry.
- `api_route_coverage_validation.py` statically greps route decorators for critical `method + path`. Its `FASTAPI_ROUTE_BASES` must list any new FastAPI route file or package.
- `field_permission_contracts.py` keeps field-level permission codes consistent across runtime code, the Django seed permission tree and the FastAPI test fixtures.
- If you change a contract, also update the tests on all three sides (Django, FastAPI, frontend) and `docs/API_ENDPOINTS.md`.

**Byte-identical file pairs.** Tests compare these files byte for byte, so edit both copies identically:
- `backend/drf_admin/apps/oauth/login_throttle_policy.py` ↔ `fastapi/app/core/login_throttle_policy.py`
- `backend/drf_admin/utils/password_policy.py` ↔ `fastapi/app/core/password_policy.py`, plus `utils/data/` ↔ `core/data/` (the SecLists common-password list, its source JSON and license)
- `backend/drf_admin/utils/avatar_validation.py` ↔ `fastapi/app/core/avatar_validation.py`

**Layering.**
- Django: `drf_admin/apps/{oauth,system,information,files}/`, each with `views/`, `serializers/`, `services/`, `filters/` and `urls.py`, mounted under `api/v1/` in `drf_admin/urls.py`. Tests sit next to the code as `test_*.py`.
- FastAPI: `app/api/v1/<module>/` routes → `app/services/system/` business logic → `app/db/models/` Tortoise models, with Pydantic models in `app/schemas/`. Large resources are split into subpackages (e.g. `api/v1/system/user_routes/` aggregated by `users.py`, and `services/system/user_services/`).

**RBAC and security boundaries.** These are enforced server-side in both backends; see the permissions section of `docs/ARCHITECTURE.md` before changing them.
- Model: users → roles → permissions (all N:M). Permission types are `CATALOG`, `MENU`, `BUTTON` and `EXTLINK`, with codes like `system:users:add`.
- Role `dataScope` (data scope) filters queries.
- Field-level read masking and write rejection are controlled by codes like `system:users:field:plain` / `system:users:field:write`.
- Delegated admins may only grant subsets of their own permissions. Writes lock the operator first, then the targets.
- After role, permission or menu changes, the permission cache must be invalidated. Django does this with signals registered in `SystemConfig.ready()`. FastAPI does it through the `access_cache` helper called from `RoleService` and `MenuService`.

**Migrations.**
- Django model changes need a complete migration chain; `validate_django_migrations.py` checks that it is tracked.
- FastAPI model changes need versioned migrations committed in `app/db/migrations/`. `generate_schemas()` only creates missing tables in dev. Production runs `migrate` once in a dedicated container or job, never inside each Uvicorn worker.

## Frontend architecture

- Menus and routes come from the backend (dynamic routing). Backend `meta` is normalized into `RouteMeta` in `src/utils/route-meta.ts`. KeepAlive keys come from `meta.cacheKey`, then the route name, and fall back to `fullPath` only for dynamic routes (`src/utils/view-cache.ts`, `store/modules/tags-view-store.ts`).
- State lives in `store/modules/user-store.ts` (auth), `permission-store.ts` (routes) and `dict-store.ts` (dictionary cache). All HTTP goes through the shared request instance in `src/utils/request.ts`, called from `src/api/`.
- Pages in `src/views` use `ProSearch` / `ProTable(request)` / `ProFormDrawer` and wire paging through `src/utils/pro-table-request.ts` (`createPageRequest` / `createListRequest`). `components/CURD` is legacy.
- Styles are layered `tokens → theme → foundation → skins → pages`. Pages compose `PageShell`, `FilterPanel` and `DataPanel`, and icons go through `components/AppIcon`.
- ADR-0001 (`docs/ADR-0001-FRONTEND-MODERNIZATION.md`) is complete. Bulk page migration is stopped, and shell or visual work must not change backend menu fields, component paths, shared APIs, or the store and Pro-component protocols.

## Documentation rules (CI-enforced)

- `AGENTS.md` and every `docs/*.md` (except `docs/archive/` and `docs/AGENT_STARTER_PROMPT.md`) must keep the `ai_summary` frontmatter (`purpose`, `read_when`, `source_of_truth`, `verify_with`, `stale_when`) and the headings `## Purpose`, `## Source of truth`, `## Key facts`, `## How to verify` and `## Stale when`.
- Every `source_of_truth` path must exist, and `verify_with` entries must be concrete commands.
- No placeholder words (`TODO`, `TBD`, `待补充`, …) and no absolute machine paths (`/Users/…`).
- `AGENTS.md` may be at most 350 lines and `docs/AI_CONTEXT.md` at most 120.
- Every relative markdown link anywhere in the repo must resolve.
- When code changes, sync the matching docs:

  | Change | Doc |
  |---|---|
  | API | `docs/API_ENDPOINTS.md` |
  | Models | `docs/DATABASE_SCHEMA.md` |
  | Architecture or flow | `docs/ARCHITECTURE.md` |
  | New pitfall | `docs/KNOWN_PITFALLS.md` |
  | Tech debt | `docs/TECH_DEBT.md` |

  The checklist is `docs/DOC_SYNC_CHECKLIST.md`. Check `docs/KNOWN_PITFALLS.md` before debugging.
