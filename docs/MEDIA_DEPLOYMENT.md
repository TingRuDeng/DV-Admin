---
ai_summary:
  purpose: "说明生产媒体持久化、旧文件复制校验和回退边界。"
  read_when:
    - "部署后端镜像或切换上传目录时"
  source_of_truth:
    - "deploy/compose.production.yml"
    - "deploy/compose.django.yml"
    - "deploy/compose.fastapi.yml"
    - "fastapi/docker/nginx.conf"
    - "scripts/verify_production_images.py"
  verify_with:
    - "python3 scripts/validate_docs.py . --profile generic"
    - "python3 scripts/verify_production_images.py"
  stale_when:
    - "媒体路径、镜像用户、卷挂载或 Nginx 路由变化"
---

# 生产媒体部署与回退

## Purpose

保证所选后端写入和 Nginx 读取同一持久卷，不修改媒体标识或数据库记录。

## Source of truth

- `deploy/compose.production.yml`、`deploy/compose.django.yml`、`deploy/compose.fastapi.yml`
- `backend/docker/Dockerfile`、`fastapi/docker/Dockerfile`、`fastapi/docker/nginx.conf`
- `scripts/verify_production_images.py`、`scripts/production_media_probe.py`

## Key facts

- 生产路径统一 `/data/media`，Django `MEDIA_ROOT` / FastAPI `UPLOAD_DIR` 指向此处；API 读写、Nginx 只读。
- URL 仍为 `/media/`，历史相对路径、头像文件名不转换。共享文件目录不代表两套后端数据库可直接互换。
- 开发默认仍是 Django `backend/drf_admin/media`、FastAPI `fastapi/uploads`。根 `compose.yaml` 仍是开发模板。
- API UID/GID 为 `10001:10001`。新空命名卷继承镜像目录所有权；现有卷不会自动修权限。
- Nginx 需要目录遍历和文件读取权限，建议目录 0755、普通媒体 0644，所有者 10001。禁止 `chmod 777`，不要给 Nginx 写权限。
- 默认公开媒体 URL 未改为授权下载；不要把密钥、项目根目录、配置或私密附件放入公开媒体目录。

## 部署入口

先选定一个后端以及独立的数据库，提供运行时环境变量；不要同时叠加两个后端覆盖文件。
`DATABASE_URL` 指向已经准备好的外部数据库，模板不会创建、复制或切换业务数据库。
初始密码配置必须符合新密码策略，真实密钥/密码不写入版本控制。
Django 还需正确设置 `ALLOWED_HOSTS`；受信反向代理用具体 IP/CIDR 配置 `TRUSTED_PROXY_IPS`，不信任全网。

```bash
# Django，先检查解析后配置；不要公开含凭据的 config 输出
docker compose -p dv-admin -f deploy/compose.production.yml -f deploy/compose.django.yml config --quiet
docker compose -p dv-admin -f deploy/compose.production.yml -f deploy/compose.django.yml up -d --build

# 或者 FastAPI，数据库 URL 和初始密码配置使用该后端的变量
docker compose -p dv-admin -f deploy/compose.production.yml -f deploy/compose.fastapi.yml config --quiet
docker compose -p dv-admin -f deploy/compose.production.yml -f deploy/compose.fastapi.yml up -d --build
```

保持 Compose project name 稳定，避免误创建另一套空卷；默认媒体卷为 `dv-admin_media`。
默认 HTTP 仅绑定宿主机 `127.0.0.1:8080`，由上层 TLS 入口接入；需要其他绑定时显式配置 `HTTP_BIND/HTTP_PORT`。
API 替换后应重启或重新加载 Nginx，使静态 upstream 名称重新解析到新容器 IP。
升级现有 `fastapi/docker/docker-compose.yml` 部署也需要先复制旧上传目录，它现已挂载同样的媒体卷。

## 旧文件迁移

1. 只读确认当前后端、实际 `MEDIA_ROOT/UPLOAD_DIR`、挂载来源、Compose project name、媒体总量及可用空间；确认目标不是其他应用或另一套数据库对应的卷。
2. 在维护窗口停止上传写入，保留旧容器/旧目录和同一时间点数据库备份。记录当前镜像摘要、环境配置及挂载关系；备份另存，不以目标卷代替备份。
3. 对旧目录创建归档，保留相对路径；逐文件记录相对路径、长度、SHA-256。排查符号链接和非普通文件，拒绝将指向目录外的链接带入媒体卷。
4. 建立空目标卷，按后端 UID/GID 10001 设置所有权；从备份复制文件并保持原相对层级。可在临时迁移容器中只读挂载旧目录、读写挂载目标卷。不要运行迁移脚本改数据库字段。
5. 对目标生成同样的逐文件清单，要求路径集合、数量、长度、SHA-256 全部一致，再检查 API 可写、Nginx 可读但不可写。不要只比较总大小。
6. 以生产模式启用新挂载，抽查旧头像/附件，上传新头像，重建 API 容器后再次下载并校验。观察权限错误、404 和日志；通过后才恢复写入。

## 回退

- 未开放新写入时，停止新容器，恢复原镜像、配置和旧媒体挂载，不删除新卷或备份。
- 已开放写入时，先再次停写，备份新卷；将新增/变更文件按相对路径和摘要与旧目录核对后回传，避免丢失新上传或覆盖较新版本。数据库与文件必须来自相容的时间点。
- 不执行 `docker compose down -v`，不自动删除旧目录，不用回滚应用镜像代替数据库回滚。

## How to verify

- quick: `python3 scripts/validate_docs.py . --profile generic`
- quick: `python3 -m unittest discover -s tests -p test_media_deployment_contracts.py`
- full: `python3 scripts/verify_production_images.py`

完整测试使用自己的临时数据库/媒体卷及 Redis，验证真实头像上传、Nginx 读取、只读挂载、503 转发及容器替换后 SHA 等价内容；不访问真实媒体或数据库。

## Stale when

- 上传目录、媒体标识、文件权限、镜像 UID 或 Nginx 配置变化。
- 编排服务名、项目名策略或备份/回退过程变化。
