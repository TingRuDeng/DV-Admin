# -*- coding: utf-8 -*-

from rest_framework.response import Response

from drf_admin.utils.views import AutoPermissionAPIView


class NoticesAPIView(AutoPermissionAPIView):
    """
    get:
    用户--获取用户拥有权限ID列表

    获取用户拥有权限ID列表, status: 200(成功), return: 用户拥有权限ID列表
    """

    def get(self, request):
        data = {
            'list': [
              {
                'id': 10,
                'title': "v2.16.1 版本修复了 WebSocket 重复连接导致的后台线程阻塞问题，优化了通知公告。",
                'type': 1,
                'level': "L",
                'publisherName': "系统管理员",
                'publishTime': "2024-09-30 17:30",
                'isRead': 0,
              },
              {
                'id': 9,
                'title': "公司将在 10 月 15 日举办新产品发布会，敬请期待。",
                'type': 5,
                'level': "L",
                'publisherName': "系统管理员",
                'publishTime': "2024-09-30 17:29",
                'isRead': 0,
              },
              {
                'id': 8,
                'title': "国庆假期从 10 月 1 日至 10 月 7 日放假，共 7 天。",
                'type': 4,
                'level': "L",
                'publisherName': "系统管理员",
                'publishTime': "2024-09-30 17:28",
                'isRead': 0,
              },
              {
                'id': 7,
                'title': "最近发现一些钓鱼邮件，请大家提高警惕，不要点击陌生链接。",
                'type': 3,
                'level': "L",
                'publisherName': "系统管理员",
                'publishTime': "2024-09-30 17:27",
                'isRead': 0,
              },
              {
                'id': 6,
                'title': "系统将于本周六凌晨 2 点进行维护，预计维护时间为 2 小时。",
                'type': 2,
                'level': "L",
                'publisherName': "系统管理员",
                'publishTime': "2024-09-30 17:26",
                'isRead': 0,
              },
            ],
            'total': 10,
          }
        return Response(data=data)
