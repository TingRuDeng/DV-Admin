from django.urls import path

from drf_admin.apps.oauth.views import home, oauth, oidc

urlpatterns = [
    path('home/', home.HomeAPIView.as_view()),
    path('info/', oauth.UserInfoView.as_view()),
    path('refresh-token/', oauth.RefreshTokenAPIView.as_view()),  # 刷新令牌接口
    path('login/', oauth.UserLoginView.as_view()),
    path('oidc/authorize/', oidc.OidcAuthorizeView.as_view()),  # 单点登录发起授权
    path('oidc/login/', oidc.OidcLoginView.as_view()),  # 单点登录回调换取本地 Token
    path('logout/', oauth.LogoutAPIView.as_view()),
    path('menus/routes/', oauth.RoutesAPIView.as_view()),  # 菜单路由列表
]
