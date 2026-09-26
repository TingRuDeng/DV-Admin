# -*- coding: utf-8 -*-

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_admin.apps.system.models import Users
from drf_admin.apps.system.services.data_scope import apply_user_data_scope

# from drf_admin.apps.monitor.models import OnlineUsers


class HomeAPIView(APIView):
    """
    get:
    系统主页--数据显示

    获取系统主页数据, status: 200(成功), return: 系统主页数据
    """

    # 用户数和用户列表同源，沿用用户查询权限；没有声明权限码时 RBAC 会拒绝所有人
    required_permissions = {"get": ["system:users:query"]}

    def get(self, request):
        data = dict()
        try:
            conn = get_redis_connection("user_info")
            visits = conn.get("visits")
            data["visits"] = int(visits.decode()) if visits else 0
        except Exception:
            data["visits"] = 0
        # 聚合同样要受数据范围约束，不能泄露范围外的用户数量
        data["users"] = apply_user_data_scope(Users.objects.all(), request.user).count()
        # data['online_users'] = OnlineUsers.objects.all().count()
        # data['assets'] = Assets.objects.all().count()
        return Response(data=data, status=status.HTTP_200_OK)
