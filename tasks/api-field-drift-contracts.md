# API 字段漂移契约一期

## 目标

把双后端响应字段漂移从隐性差异变成可评审、可回归的显式清单。本轮不统一字段、不改运行时 API，只冻结首批高价值响应对象的字段集合：已登记差异允许通过，新增未登记字段漂移触发测试失败。

## 执行清单

- [x] P1 串行：新增共享 API 字段契约目录，冻结首批字段漂移面。
- [x] P2 串行：新增 Django/FastAPI 字段契约测试，阻断未登记字段漂移。
- [x] P3 串行：扩展 API 契约校验器，校验字段契约自洽、证据和测试挂钩。
- [x] P4 串行：执行文档、契约、Django、FastAPI 和 diff 验证，完成 review-gate。

## 并行评估

本轮不启用 subagent。字段契约目录、两端测试和根校验器互相依赖，且都围绕同一组契约 key 演进；串行实现可以避免契约清单与测试断言不同步。

## 验证计划

- `python3 scripts/validate_api_contracts.py .`
- `python3 scripts/validate_docs.py . --profile generic`
- `cd backend && uv run pytest drf_admin/utils/test_api_field_contracts.py drf_admin/utils/test_response_contract.py`
- `cd fastapi && uv run pytest tests/test_api_field_contracts.py tests/test_api_contracts.py`
- `git diff --check`

## Review 小结

- Review-gate：finished；Spec 符合度通过，本轮只新增字段漂移显式契约、双后端字段测试和根契约校验入口，不改变运行时 API、数据库结构或前端行为；安全检查未发现本轮新增 secret；复杂度检查通过，新增文件均小于 300 行；Document-refresh: done，`docs/API_ENDPOINTS.md` 已补充字段契约入口；剩余风险是首批清单只覆盖系统管理高价值对象，后续新增响应对象仍需继续纳入字段契约目录。
