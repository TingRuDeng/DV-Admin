# project-context-bootstrap 上下文文档升级

- [x] 确认当前仓库已有旧文档体系，采用升级模式而不是重建模式
- [x] 核对项目技术栈，确认当前仓库不是 Android 项目，使用 generic profile
- [x] 升级核心上下文文档入口和 AI 短上下文地图
- [x] 升级上下文包校验脚本
- [x] 运行校验并修复失败项
- [x] 完成交付前审查

## Review 小结

终态：finished。已按升级模式保留旧文档主体，补齐上下文包契约；`python3 scripts/validate_docs.py . --profile generic` 与 `python3 -m py_compile scripts/validate_docs.py` 均通过。

---

# P3 前端直接 console 收口

- [x] 新增全量直接 `console.*` 治理测试，并先确认当前代码会失败
- [x] 为剩余 SFC/组件引入 `createLogger` 并替换直接 `console.warn/error`
- [x] 运行目标测试，确认治理测试由红转绿
- [x] 运行前端质量、构建、smoke 和文档校验
- [x] 使用 `review-gate` 做交付前审查

## Review 小结

终态：finished。P3 已将生产前端源码剩余直接 `console.*` 收口到 `createLogger`，并新增 `direct-console-governance` 守卫测试；前端质量、生产构建、登录 smoke、文档校验和 diff 检查均通过。
