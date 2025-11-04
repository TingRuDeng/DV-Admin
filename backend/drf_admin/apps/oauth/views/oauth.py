# -*- coding: utf-8 -*-

import json
import logging

from django.conf import settings
from rest_framework import status
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from django_redis import get_redis_connection
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_admin.apps.system.models import Permissions, Users
from drf_admin.apps.oauth.serializers.token_serializers import CustomTokenObtainPairSerializer

logger = logging.getLogger('info')


class UserLoginView(TokenObtainPairView):
    """
    post:
    用户登录

    用户登录, status: 200(成功), return: Token信息
    """
    throttle_classes = [AnonRateThrottle]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # 重写父类方法, 定义响应字段内容
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            data = {
                'accessToken': response.data['access'],
                'refreshToken': response.data['refresh']  # 可选
            }
            # 检查Redis配置是否存在
            if hasattr(settings, 'REDIS_HOST') and hasattr(settings, 'REDIS_PORT') and settings.REDIS_HOST and settings.REDIS_PORT:
                try:
                    conn = get_redis_connection('user_info')
                    conn.incr('visits')
                except Exception as e:
                    logger.error(f"Redis connection error: {str(e)}")
            else:
                # 使用Django缓存代替Redis特定功能
                cache_key = 'visits'
                current_count = cache.get(cache_key, 0)
                cache.set(cache_key, current_count + 1)
            return Response(data)
        else:
            if response.data.get('non_field_errors'):
                # 日后将增加用户多次登录错误,账户锁定功能(待完善)
                if isinstance(response.data.get('non_field_errors'), list) and len(
                        response.data.get('non_field_errors')) > 0:
                    if response.data.get('non_field_errors')[0].strip() == '无法使用提供的认证信息登录。':
                        return Response(data={'detail': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)
            raise ValidationError(response.data)


class UserInfoView(APIView):
    """
    get:
    当前用户信息和权限

    当前用户信息, status: 200(成功), return: 用户信息和权限
    """

    def get(self, request):
        user_info = request.user.get_user_info()
        http_host = request.get_host()
        http_port = request.get_port()
        if http_port in http_host:
            host_url = f'{request.scheme}://{http_host}'
        else:
            host_url = f'{request.scheme}://{http_host}:{http_port}'
        # 检查Redis配置是否存在
        if hasattr(settings, 'REDIS_HOST') and hasattr(settings, 'REDIS_PORT') and settings.REDIS_HOST and settings.REDIS_PORT:
            try:
                # 尝试使用Redis缓存
                conn = get_redis_connection('user_info')
                if request.user.is_superuser and 'admin' not in user_info['perms']:
                    user_info['perms'].append('admin')
                user_info['perms'] = json.dumps(user_info['perms'])
                user_info[
                    'avatar'] = f'{host_url}{user_info.get("avatar")}'
                conn.hmset(f'user_info_{request.user.id}', user_info)
                conn.expire(f'user_info_{request.user.id}', 60 * 60 * 24)  # 设置过期时间为1天
                user_info['perms'] = json.loads(user_info['perms'])
            except Exception as e:
                logger.error(f"Redis connection error: {str(e)}")
        else:
            # Redis不可用时，使用Django缓存存储用户信息
            if request.user.is_superuser and 'admin' not in user_info['perms']:
                user_info['perms'].append('admin')
            user_info[
                'avatar'] = f'{host_url}{user_info.get("avatar")}'
            cache_key = f'user_info_{request.user.id}'
            cache.set(cache_key, user_info, 60 * 60 * 24)
        return Response(user_info, status=status.HTTP_200_OK)


class RoutesAPIView(APIView):
    """
    get:
    菜单--获取用户拥有菜单列表，由前端组合成动态路由

    获取用户拥有菜单列表, status: 200(成功), return: 用户拥有菜单列表
    """

    def get(self, request):
        try:
            user = Users.objects.get(id=request.user.id, is_active=True)
        except Permissions.DoesNotExist:
            raise ValidationError('无效的用户ID')
        # admin角色
        # if 'admin' in user.roles.values_list('name', flat=True) or user.is_superuser:
        #     return Response(data={'results': Permissions.objects.values_list('id', flat=True)})
        # 其他角色
        return Response(data=user.get_menus())


class LogoutAPIView(APIView):
    """
    post:
    退出登录

    退出登录, status: 200(成功), return: None
    """

    def post(self, request):
        content = {}
        # 后续将增加redis token黑名单功能
        return Response(data=content)