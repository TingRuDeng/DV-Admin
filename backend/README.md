## 简介
基于RBAC模型权限控制的中小型应用的基础开发平台，前后端分离。`backend/` 是项目的 Django 后端实现，对应的替代实现见 `fastapi/`。两者面向同一套前端和业务域，日常开发/部署通常二选一。

JWT认证,可使用simple_history实现审计功能,支持 Swagger API 文档

### Swagger API 文档

启动服务后，可通过以下地址访问 API 文档：

- Swagger UI: http://127.0.0.1:8769/api/v1/swagger/
- ReDoc: http://127.0.0.1:8769/api/v1/redoc/

> 注意：需要在 `.env.dev` 中设置 `ENABLE_SWAGGER=True` 启用 Swagger（默认关闭）

-----

## 前置准备
```angular2html
Python >= 3.11.0（如多版本环境推荐使用pyenv进行管理）
Mysql >= 8.0 (可选，默认数据库sqlite3，支持5.7+，推荐8.0版本)
Redis (最新版，可选)
```

### Redis
```shell
  # 启动服务：
  redis-server --service-start
  
  # 停止服务：
  redis-server --service-stop
  
  # 卸载服务：
  redis-server --service-uninstall
```


-----

## 开发环境说明（以下为Mac/Linux下的操作步骤）
### 环境配置
```bash
# 1、切换到后端根目录
cd backend

# 2、安装python环境管理工具uv
## windows下安装
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

## Mac/Linux下安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3、复制 .env.example 为 .env.dev 并按实际需求更改文件配置参数
cp .env.example .env.dev

# 4、生成数据库迁移文件
uv run python manage.py makemigrations oauth system --env dev

# 5、迁移数据库，--env dev 表示使用 .env.dev 配置文件
uv run python manage.py migrate --env dev

# 6、导入初始数据
uv run python manage.py loaddata init_data.json --env dev
  
# 7、启动服务（推荐使用脚本，自动检测环境、安装依赖）
./dev.sh start

# 查看服务状态
./dev.sh status

# 查看实时日志
./dev.sh logs

# 停止服务
./dev.sh stop
```

### 使用脚本管理服务（推荐）

```bash
# 启动服务（自动检测 uv、安装依赖、创建虚拟环境）
./dev.sh start

# 启动指定环境
./dev.sh start --env=test

# 查看服务状态
./dev.sh status

# 查看实时日志
./dev.sh logs

# 停止服务
./dev.sh stop

# 重启服务
./dev.sh restart
```

### 手动启动（不推荐）

```bash
# 创建虚拟环境并安装依赖
uv venv
uv sync

# 运行服务
uv run python manage.py runserver 0.0.0.0:8769 --env dev
```

### 2、账户、角色、权限
* Django 初始化数据库基础数据后，会生成2个账户、2个角色、项目权限

### 3、账户
* admin/123456，(admin为用户名，123456为密码，该账户为超级管理员用户，具有项目所用权限)
* visitor/123456，(visitor为用户名，123456为密码，该账户为测试访客用户，具有项目部分权限)

### 4、角色
* admin，(admin角色，默认拥有项目所有权限；可给用户授予角色来给用户配置权限)
* visitor，(visitor角色，默认拥有项目部分权限；可给用户授予角色来给用户配置权限)


## 质量检查与测试

```bash
# 安装开发依赖
uv sync --group dev

# 代码风格检查 (Ruff)
uv run ruff check .

# 运行测试 (pytest)
uv run pytest
```

- 问题1：环境同步异常，提示文件路径过长、could not create ... No such file or directory
    > 这是由于 Windows 默认的路径长度限制（MAX_PATH）导致的，尤其是当路径嵌套较深时 
    >
    > 解决方案：启用长路径支持​
    > 
    > - 在 Windows 搜索框输入“注册表编辑器”并打开；
    > - 导航到 计算机\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem；
    > - 找到 LongPathsEnabled项，双击将其值从 0改为 1。如果不存在，则右键新建一个 DWORD (32位)值，命名为 LongPathsEnabled，并设置值为 1；
    > - 重启电脑使设置生效。

- 问题2：执行uv run python manage.py migrate --env dev 报错
  > 解决方法：删除drf_admin/apps/各应用目录下的所有migrations文件夹
  > 
  > linux下可执行命令：find ./ -type d -name "migrations"|grep -v "venv" |xargs rm -rf
  > 
  > windows下可执行命令：dir /s /b /ad migrations | findstr /v venv | xargs rd /s /q
  > 执行完成后，再次从 环境配置 第5步开始往下执行
