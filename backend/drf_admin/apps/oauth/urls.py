from django.urls import path

from drf_admin.apps.oauth.views import home, oauth
from drf_admin.apps.oauth.views.registration import (
    CaptchaAPIView,
    EmailCodeAPIView,
    PasswordResetAPIView,
    RegisterAPIView,
)

urlpatterns = [
    path('home/', home.HomeAPIView.as_view()),
    path('info/', oauth.UserInfoView.as_view()),
    path('refresh-token/', oauth.RefreshTokenAPIView.as_view()),  # 刷新令牌接口
    path('login/', oauth.UserLoginView.as_view()),
    path('logout/', oauth.LogoutAPIView.as_view()),
    path('menus/routes/', oauth.RoutesAPIView.as_view()),  # 菜单路由列表
    path('captcha/', CaptchaAPIView.as_view()),
    path('email-code/', EmailCodeAPIView.as_view()),
    path('register/', RegisterAPIView.as_view()),
    path('password/reset/', PasswordResetAPIView.as_view()),
]
