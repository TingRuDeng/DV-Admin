"""媒体路由注册测试。"""

from importlib import reload

from django.test import override_settings

import drf_admin.urls


@override_settings(DEBUG=True, ENABLE_SWAGGER=False)
def test_media_urls_registered_when_debug_without_swagger():
    """开发环境媒体路由不应依赖 Swagger 开关。"""
    urls = reload(drf_admin.urls)
    try:
        patterns = [str(pattern.pattern) for pattern in urls.urlpatterns]
        assert any("media/" in pattern for pattern in patterns)
        assert not any("swagger" in pattern for pattern in patterns)
    finally:
        reload(drf_admin.urls)
