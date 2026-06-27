# 五项审查建议处理记录

## 目标

按已批准计划处理五项架构审查建议：先收口 FastAPI 生产 API 文档暴露，再清理无后端契约的前端死代码，随后修正文档事实、登记操作日志能力缺口，并调整治理规则避免继续以纯行数为主导。

## 执行清单

- [x] P1 串行：关闭 FastAPI 生产环境 API 文档暴露并补回归测试。
- [x] P2 串行：删除 `frontend/src/api/test/` 死代码并调整前端治理测试。
- [x] P3 串行：修正数据库字段事实和操作日志双后端能力缺口文档。
- [x] P4 串行：调整治理规则，降低纯行数导向。
- [x] P5 串行：执行文档、契约、FastAPI、前端和 diff 验证，完成 review-gate。

## 并行评估

本轮不启用 subagent。原因是改动文件集中在同一组权威文档、任务状态和契约说明上，多个写入任务之间存在语义依赖；串行推进可以降低文档事实互相覆盖或表述不一致的风险。

## 验证计划

- `python3 scripts/validate_docs.py . --profile generic`
- `python3 scripts/validate_api_contracts.py .`
- `python3 scripts/validate_model_contracts.py .`
- `make -C fastapi quality`
- `pnpm --dir frontend run quality`
- `pnpm --dir frontend run build`
- `rg "api/test|cases-api|project-api|device\\.api|task\\.api" frontend/src -n`
- `git diff --check`

## Review 小结

- FastAPI 生产环境 API 文档入口已通过 `get_api_docs_config(settings.is_production)` 统一收口，新增测试覆盖生产关闭和非生产保留两个分支。
- `frontend/src/api/test/` 四个无后端契约的示例 API 文件已删除，治理测试不再扫描已删除文件，死代码扫描无命中。
- `docs/API_ENDPOINTS.md`、`docs/DATABASE_SCHEMA.md`、`docs/ARCHITECTURE.md` 和 `docs/TECH_DEBT.md` 已明确操作日志当前为 FastAPI 独有能力，Django 仅有文件日志中间件。
- `AGENTS.md`、`docs/FRONTEND_OPTIMIZATION_BACKLOG.md` 和 `docs/TECH_DEBT.md` 已把后续治理优先级调整为契约缺口、能力漂移、安全配置、死代码、文档事实冲突和测试盲区，300 行仅作为风险提示。
- 验证通过：`python3 scripts/validate_docs.py . --profile generic`、`python3 scripts/validate_api_contracts.py .`、`python3 scripts/validate_model_contracts.py .`、`make -C fastapi quality`、`pnpm --dir frontend run quality`、`pnpm --dir frontend run build`、死代码扫描和 `git diff --check`。
- review-gate 结论：未发现阻断项；剩余风险是 Django 操作日志能力缺口仍未实现，已登记为高优先级技术债。
