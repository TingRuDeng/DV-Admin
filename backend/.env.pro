# 生产环境配置文件
# 注意：不要将此文件提交到版本控制系统

# Django 核心配置
DEBUG=False
SECRET_KEY='mod1q7pk7hh)da39+yc1$^1codec)$lt69*wp1rdz_mja4yaa'  # 请设置一个强密钥
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
# PostgreSQL 配置示例
# DATABASE_URL=postgres://username:password@localhost:5432/dbname
# 或者 MySQL 配置示例
# DATABASE_URL=mysql://username:password@localhost:3306/dbname?charset=utf8mb4

# Redis 配置，生产环境请设置密码
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PWD=

# CORS 配置，生产环境请使用域名
CORS_ALLOWED_ORIGINS=http://localhost:9527,http://127.0.0.1:9527

# 新增用户默认密码，生产环境请设置一个安全的默认密码
DEFAULT_PWD=123456

# 安全设置，生产环境请全部打开
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# JWT配置
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7