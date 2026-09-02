# Django 测试配置
# 默认使用 SQLite 内存数据库；真实浏览器 smoke 使用临时文件数据库
import os
import tempfile
from pathlib import Path

# 设置环境变量
os.environ.setdefault('ENVIRONMENT', 'test')

# 现在导入 settings
from drf_admin.settings import *

# 覆盖数据库配置使用 SQLite 内存数据库
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {
            "NAME": (
                str(
                    Path(tempfile.gettempdir())
                    / f"dv_admin_django_live_smoke_{os.getpid()}.sqlite3"
                )
                if os.environ.get("RUN_REAL_BACKEND_PLAYWRIGHT") == "1"
                else ":memory:"
            ),
        },
    }
}

# 关闭调试模式
DEBUG = False

# 简化权限检查 - 测试时允许所有请求
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.AllowAny",
]
if os.environ.get("RUN_REAL_BACKEND_PLAYWRIGHT") == "1":
    # 一次 Playwright 套件会创建多个隔离登录会话；限流本身由专门测试覆盖。
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"] = "100/min"

# 测试运行器
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# 简化密码哈希（加快测试速度）
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
