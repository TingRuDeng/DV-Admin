from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from drf_admin.apps.oauth.views import oauth, home

urlpatterns = [
    path('home/', home.HomeAPIView.as_view()),
    path('info/', oauth.UserInfoView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('login/', oauth.UserLoginView.as_view()),
    path('logout/', oauth.LogoutAPIView.as_view()),
    path('menus/routes/', oauth.RoutesAPIView.as_view()),  # 菜单路由列表
]
