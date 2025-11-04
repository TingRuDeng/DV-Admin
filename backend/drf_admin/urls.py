"""drf_admin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.decorators.clickjacking import xframe_options_exempt

from drf_admin.settings import DEBUG, env

# swagger API文档配置 https://github.com/axnsan12/drf-yasg
schema_view = get_schema_view(
    openapi.Info(
        title="DRF Admin API",
        default_version='v1.0.0',
        description="平台api接口文档",
        license=openapi.License(name="BSD License"),
    ),
    public=True,  # 是否公开文档（无需认证可访问）
    permission_classes=([permissions.AllowAny,]),  # 访问文档的权限
)

base_api = settings.BASE_API

urlpatterns = [
    # 加载项目模块
    path(f'{base_api}oauth/', include('drf_admin.apps.oauth.urls')),  # 用户鉴权模块
    path(f'{base_api}system/', include('drf_admin.apps.system.urls')),  # 系统管理模块
    path(f'{base_api}information/', include('drf_admin.apps.information.urls')),  # 个人中心模块
]

EXTRA_ROUTES = [path(f'{base_api}{route}/', include(f'drf_admin.apps.{route}.urls')) for route in env.list('EXTRA_INSTALLED_APPS', default=[])]

# 添加额外的路由到 urlpatterns
urlpatterns.extend(EXTRA_ROUTES)

# 仅在非生产环境添加 Swagger 文档 URL
if DEBUG:
    urlpatterns += [
        re_path(rf'^{base_api}swagger(?P<format>\.json|\.yaml)$',
                xframe_options_exempt(schema_view.without_ui(cache_timeout=0)), name='schema-json'),
        path(f'{base_api}swagger/',
             xframe_options_exempt(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
        path(f'{base_api}redoc/',
             xframe_options_exempt(schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
