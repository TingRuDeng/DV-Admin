## 项目简介

基于 Vue3、Vite7、TypeScript 和 Element-Plus 搭建的极简开箱即用企业级后台管理前端模板。 

## 项目启动

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
- 如果你修改了后端端口，需要同步更新 [frontend/.env.development](/Users/dengtingru/Desktop/code/DV-Admin/frontend/.env.development) 中的 `VITE_APP_API_URL`
- 默认可用账户：
  - `admin/123456`
  - `visitor/123456`

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

# 构建（包含类型检查）
pnpm run build

# 代码提交（请在提交前先执行 pnpm run quality 检查代码是否符合规范）
pnpm run commit
```


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
}
```
