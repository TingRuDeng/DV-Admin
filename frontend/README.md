## 项目简介

基于 Vue3、Vite7、TypeScript 和 Element-Plus 搭建的极简开箱即用企业级后台管理前端模板。 

## 项目启动

> 开发与构建要求 Node.js `>=24.0.0`；项目通过 `packageManager` 固定使用 pnpm `11.21.0`。

- **快速开始（推荐使用脚本）**

```bash
# 切换目录
cd frontend

# 启动服务（后台运行，自动检测环境、安装依赖）
./dev.sh start

# 查看服务状态
./dev.sh status

# 停止服务
./dev.sh stop

# 重启服务
./dev.sh restart
```

- **手动启动**

```bash
# 切换目录
cd frontend

# 安装 pnpm
npm install pnpm -g

# 设置镜像源(可选)
pnpm config set registry https://registry.npmmirror.com

# 安装依赖
pnpm install

# 启动运行
pnpm run dev
```

## 本地联调说明

- 前端开发服务器默认运行在 `http://localhost:9527`
- 开发环境下，前端会将 `/dev-api` 代理到 `http://127.0.0.1:8769`
- 本地联调时，请在 Django `backend/` 和 FastAPI `fastapi/` 两套后端实现中选择一套启动即可
- 如果你修改了后端端口，需要同步更新 [.env.development](.env.development) 中的 `VITE_APP_API_URL`
- 开发种子数据默认可用账户：
  - `admin/123456`
  - `visitor/123456`
- 登录/注册表单不会在生产或预发环境硬编码预填账号密码；本地演示预填由 [.env.development](.env.development) 中的 `VITE_LOGIN_DEFAULT_USERNAME` 与 `VITE_LOGIN_DEFAULT_PASSWORD` 显式控制

## 质量检查命令

```bash
# 代码检查（lint + prettier + stylelint）
pnpm run lint

# 类型检查
pnpm run type-check

# 单元测试
pnpm run test:unit

# 统一质量门禁（lint + type-check + test:unit）
pnpm run quality

# 生产依赖安全审计（阻断未豁免的 high/critical 公告）
pnpm run audit:prod

# 构建（包含类型检查）
pnpm run build

# 双后端真实浏览器 smoke（从仓库根目录运行其一；测试会启动隔离后端和 Vite）
(cd backend && RUN_REAL_BACKEND_PLAYWRIGHT=1 .venv/bin/pytest \
  drf_admin/utils/runtime_api_contracts/test_live_http_contract.py::DjangoLiveHttpContractTestCase::test_shared_frontend_flow_over_real_django_http)
(cd fastapi && RUN_REAL_BACKEND_PLAYWRIGHT=1 .venv/bin/pytest \
  tests/test_live_http_contract.py::test_shared_frontend_flow_over_real_fastapi_http)

# 代码提交（请在提交前先执行 pnpm run quality 检查代码是否符合规范）
pnpm run commit
```

真实后端 smoke 不拦截 API；同一份 Playwright 流程会分别连接 Django LiveServer 与
FastAPI Uvicorn，使用隔离数据库和临时上传目录。日常前端 Mock E2E 仍由
`pnpm run test:e2e:smoke` 执行。

`audit:prod` 会实时读取 pnpm 公告。临时豁免仅允许登记在
`dependency-audit-exemptions.json`，必须限定公告、包、依赖路径、责任人和到期日期；
到期豁免或同一公告出现新的依赖路径都会使门禁失败。

如果 npm advisory bulk 接口临时不可用，CI 只能通过独立的
`dependency-audit-network-exception.json` 对明确范围的 PR 做限期放行。该例外只处理
审计请求超时，审计结果一旦返回仍会执行 high/critical 门禁；到期后脚本自动失败，且
生产发布前必须重新取得一份成功的实时审计报告。网络恢复后应删除例外配置及 workflow
中的临时条件，不得把网络例外写入漏洞公告豁免文件。


## 项目部署

执行 `pnpm run build` 命令后，项目将被打包并生成 `dist` 目录。接下来，将 `dist` 目录下的文件上传到服务器 `/usr/share/nginx/html` 目录下，并配置 Nginx 进行反向代理。

```bash
pnpm run build
```

以下是 Nginx 的配置示例：

```nginx
server {
    listen      80;
    server_name localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    # 反向代理配置
    location /prod-api/ {
        proxy_pass http://api.xxxx.com/;
    }

    # 后端返回 /media/... 相对路径时需要同源转发
    location /media/ {
        proxy_pass http://api.xxxx.com/media/;
    }
}
```
