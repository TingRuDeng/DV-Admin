"""Django Channels ASGI 路由入口。

HTTP 继续复用 Django ASGI 应用；当前仓库没有业务 WebSocket 路由，
但保留明确的 Channels 入口，避免 `ASGI_APPLICATION` 指向不存在模块。
"""

from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_admin.settings")

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter([])),
    }
)
