# Django 测试配置
# 使用 SQLite 内存数据库进行测试
import os

# 设置环境变量
os.environ.setdefault('ENVIRONMENT', 'test')

# 现在导入 settings
from drf_admin.settings import *

# 覆盖数据库配置使用 SQLite 内存数据库
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# 关闭调试模式
DEBUG = False

# 简化权限检查 - 测试时允许所有请求
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.AllowAny",
]

# 测试运行器
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# 简化密码哈希（加快测试速度）
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
