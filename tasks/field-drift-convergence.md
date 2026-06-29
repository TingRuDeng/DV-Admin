# 字段漂移全量收敛

## 目标

- 按已确认六阶段计划清理 Django / FastAPI 共享 API 字段漂移。
- 每阶段都同步字段契约、前端字段契约、技术债与必要测试。
- 最终让 `scripts/api_field_contracts.py` 中需要收敛的 `converge` 清单清零。

## 非目标

- 不处理 Django 操作日志能力缺口。
- 不迁移数据库物理字段命名。
- 不为通过测试引入静默 fallback 或 mock 成功路径。

## 当前事实

- 字段漂移目录位于 `scripts/api_field_contracts.py`。
- 技术债跟踪位于 `docs/TECH_DEBT.md`。
- 通知分页字段 `targetUserIds/updateTime` 已在上一轮收敛。

## 执行计划

- [x] 阶段 1：收敛用户/角色字段 `roleNames`、`roles`、`rolesList`、`permissions`。
- [x] 阶段 2：收敛菜单父级和树字段 `parent`、`parentId`、`children`、`label`。
- [ ] 阶段 3：收敛部门树字段 `children`、`parentName` 与部门时间字段。
- [ ] 阶段 4：收敛字典项展示字段 `dictName`，并梳理字典字段。
- [ ] 阶段 5：统一时间字段策略 `createTime/updateTime` 与 `createdAt/updatedAt`。
- [ ] 阶段 6：复核非 `converge` 单端扩展字段并清理技术债。

## 进度记录

- 开始执行：当前分支 `codex/frontend-field-contracts`，工作区干净。
- 阶段 1 现状：Django 用户输出有 `roles/rolesList`，FastAPI 用户输出有 `roleNames/roles`；Django 角色分页有 `permissions`，FastAPI 角色详情有 `permissions` 但分页缺失。
- 阶段 1 红灯测试：补充 FastAPI 用户分页/表单角色字段测试，以及角色分页 `permissions` 测试。
- 阶段 1 实现：用户输出统一提供 `roles` 与 `roleNames`，角色分页统一提供 `permissions`；`rolesList` 暂作为 Django 旧扩展字段保留到第 6 阶段复核。
- 阶段 2 红灯测试：补充 FastAPI 菜单树 `label/children/parent_id` 和详情 `parent_id` 断言。
- 阶段 2 实现：菜单对外父级字段统一为 `parentId`，FastAPI 菜单树补 `label`，Django 菜单 serializer 显式输出并接收 `parentId`。
