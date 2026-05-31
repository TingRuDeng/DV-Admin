# FastAPI 依赖锁定治理计划

## 目的

消除 FastAPI 本地依赖解析与 GitHub Actions 依赖解析不一致的问题，避免再次出现“本地验证通过、远端 CI 失败”的漂移。

## 适合读者

- 维护 FastAPI 后端质量门禁的开发者
- 执行依赖升级、CI 修复或后端验证的 AI 代理

## 一分钟摘要

- `fastapi/uv.lock` 已存在本地，但此前被全局 Git ignore 规则忽略，没有进入仓库。
- CI 因拿不到锁文件，会重新解析依赖，可能得到比本地更新的 `mypy`、`redis`、`tortoise-orm` 组合。
- 本轮将 `fastapi/uv.lock` 纳入仓库，并在 `.gitignore` 显式解除全局 ignore 的影响。

## ai_summary

```yaml
purpose: "记录 FastAPI uv.lock 纳入仓库的原因、边界和验证方式。"
read_when:
  - "处理 FastAPI 依赖、CI 或本地验证漂移时"
  - "升级 FastAPI Python 依赖前"
source_of_truth:
  - "fastapi/pyproject.toml"
  - "fastapi/uv.lock"
  - ".github/workflows/quality-gates.yml"
verify_with:
  - "cd fastapi && uv lock --check"
  - "cd fastapi && uv sync --locked --group dev"
  - "cd fastapi && make quality"
stale_when:
  - "FastAPI 包管理器从 uv 切换到其他工具"
  - "CI 不再使用 uv sync --group dev"
```

## 权威边界

- 本文件只记录 FastAPI 依赖锁定治理，不定义业务接口、数据库模型或前端依赖策略。
- FastAPI 依赖声明以 `fastapi/pyproject.toml` 为准，解析结果以 `fastapi/uv.lock` 为准。

## 如何验证

1. `git check-ignore -v fastapi/uv.lock` 不应再返回全局 ignore 命中。
2. `git ls-files fastapi/uv.lock` 应能看到锁文件已被仓库跟踪。
3. `cd fastapi && uv lock --check` 应通过。
4. `cd fastapi && uv sync --locked --group dev` 应通过。
5. `cd fastapi && make quality` 应通过。

## 执行清单

- [x] 在 `.gitignore` 中显式解除 `fastapi/uv.lock` 的全局 ignore 影响。
- [x] 将 `fastapi/uv.lock` 纳入仓库。
- [x] 运行 FastAPI 锁文件与质量门禁验证。
- [x] 提交并创建 PR。

## Review 小结

终态：finished。`fastapi/uv.lock` 已纳入仓库，`.gitignore` 已显式解除全局 `uv.lock` ignore 对本项目 FastAPI 锁文件的影响；锁文件检查、锁定安装、FastAPI 质量门禁、文档校验、脚本编译和暂存 diff 检查均已通过。
