# -*- coding: utf-8 -*-

from django.urls import path

from drf_admin.apps.information.views import centre

urlpatterns = [
    path('change-password/', centre.ChangePasswordAPIView.as_view()),  # 修改个人密码
    path('change-information/', centre.ChangeInformationAPIView.as_view()),  # 修改个人信息
    path('change-avatar/', centre.ChangeAvatarAPIView.as_view()),  # 修改个人头像
]
