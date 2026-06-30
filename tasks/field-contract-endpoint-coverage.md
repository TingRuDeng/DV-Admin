# 字段契约覆盖写端点与鉴权端点

## 目标

- 将字段契约覆盖从读端点扩展到有对象响应的写端点。
- 将 `auth_info` 与 `auth_routes` 纳入字段契约和前端类型契约。
- 保留 FastAPI 独占能力和非业务对象响应的显式豁免。

## 非目标

- 不修复已登记的字段漂移。
- 不修改 Django / FastAPI 业务响应字段。
- 不补 Django 操作日志能力。

## 执行计划

- [x] RED：补字段契约覆盖测试。
- [x] 扩展字段来源读取能力。
- [x] 补端点字段契约映射与豁免。
- [x] 补前端字段契约。
- [x] 执行验证与 review-gate。

## 进度记录

- 开始执行：分页修复已提交，当前工作区干净。
- RED：Django / FastAPI 字段契约测试先因缺少 `iter_endpoint_field_contracts` 失败，证明覆盖守卫缺口被测试捕获。
- 实现：新增 `auth_info`、`auth_routes` 字段契约；端点覆盖扩展到有对象响应的 create/update；`auth_login`、`files_upload`、`logs_page` 显式豁免。
- 字段来源：新增 AST 读取工具，支持 Django 方法直接返回 dict、FastAPI helper 构造 dict，不为测试硬造 serializer。
- 验证：后端字段契约、Django runtime contract、FastAPI quality、前端 quality、根契约和文档校验均通过。

## Review 小结

- 本轮只扩展契约覆盖和守卫，不修复已登记的字段漂移。
- `auth_info` 当前记录 FastAPI 独有 `createdAt/updatedAt/deptId/isActive`，只冻结现状，不做字段统一。
