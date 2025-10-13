## 项目简介

基于 Vue3、Vite7、TypeScript 和 Element-Plus 搭建的极简开箱即用企业级后台管理前端模板。 

## 项目启动

- **快速开始**

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

# 代码检查
pnpm run lint

# 代码提交（请在提交前先执行 pnpm run lint 检查代码是否符合规范）
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
