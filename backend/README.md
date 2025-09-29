## 简介
基于RBAC模型权限控制的中小型应用的基础开发平台,前后端分离,后端采用django+django-rest-framework,前端采用vue+ElementUI。

JWT认证,可使用simple_history实现审计功能,支持swagger

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

# 安装python环境管理工具uv
## windows下安装
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

## Mac/Linux下安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3、Python虚拟环境及依赖包安装（根据 pyproject.toml 解析并安装相关依赖）
uv sync

# 4、复制 .env.example 为 .env.dev 并按实际需求更改文件配置参数
cp .env.example .env.dev

# 5、生成数据库迁移文件
uv run python manage.py makemigrations oauth system --env dev

# 6、迁移数据库，--env dev 表示使用 .env.dev 配置文件，默认使用该配置则后续命令都可不加
uv run python manage.py migrate --env dev

# 7、导入初始数据
uv run python manage.py loaddata init_data.json --env dev
  
# 8、运行服务（如后端使用其他启动端口，则需修改前端配置文件 .env.development 中的端口值） 
## 开发环境运行
uv run python manage.py runserver 0.0.0.0:8769 --env dev

## 测试/开发环境运行(启停服务)
./service.sh start
./service.sh stop
./service.sh restart

# 9、如需求读取其他环境配置文件如 .env.test，可在命令后添加 --env test
uv run python manage.py runserver 0.0.0.0:8769 --env test
```

### 2、账户、角色、权限
* Django 初始化数据库基础数据后，会生成2个账户、2个角色、项目权限

### 3、账户
* admin/123456，(admin为用户名，123456为密码，该账户为超级管理员用户，具有项目所用权限)
* visitor/123456，(visitor为用户名，123456为密码，该账户为测试访客用户，具有项目部分权限)

### 4、角色
* admin，(admin角色，默认拥有项目所有权限；可给用户授予角色来给用户配置权限)
* visitor，(visitor角色，默认拥有项目部分权限；可给用户授予角色来给用户配置权限)


## 问题汇总

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
