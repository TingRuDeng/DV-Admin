# -*- coding: utf-8 -*-

import json
import logging

from rest_framework import status
from rest_framework.response import Response
from django_redis import get_redis_connection
from django.utils.deprecation import MiddlewareMixin

# from drf_admin.apps.monitor.models import OnlineUsers
from drf_admin.apps.oauth.utils import get_request_browser, get_request_os, get_request_ip


class OperationLogMiddleware:
    """
    操作日志Log记录
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.operation_logger = logging.getLogger('operation')  # 记录非GET操作日志
        self.query_logger = logging.getLogger('query')  # 记录GET查询操作日志

    def __call__(self, request):
        request_body = dict()
        content_type = request.META.get('CONTENT_TYPE', '')
        try:
            if 'application/json' in content_type and request.body != b'':
                request_body = json.loads(request.body)
                if not isinstance(request_body, dict):
                    request_body = dict()
        except Exception as e:
            logging.error(f'JSON解析请求体失败: {e}，请求url：{request.path}')
        if request.method == "GET":
            request_body.update(dict(request.GET))
            logger = self.query_logger
        else:
            request_body.update(dict(request.POST))
            logger = self.operation_logger
        # 处理密码, log中密码已******替代真实密码
        for key in request_body:
            if 'password' in key:
                request_body[key] = '******'
        response = self.get_response(request)
        try:
            # 修复: 首先检查response是否有data属性
            if hasattr(response, 'data'):
                response_body = response.data
                # 处理token, log中token已******替代真实token值
                if isinstance(response_body, dict) and 'data' in response_body:
                    if isinstance(response_body['data'], dict):
                        if response_body['data'].get('accessToken'):
                            response_body['data']['accessToken'] = '******'
                        if response_body['data'].get('refreshToken'):
                            response_body['data']['refreshToken'] = '******'
            else:
                # 对于没有data属性的响应类型(如静态文件)
                response_body = dict()
        except Exception as e:
            logging.error(f'日志敏感信息覆写失败: {e}, 请求URL：{request.path}')
            response_body = dict()

        request_ip = get_request_ip(request)
        log_info = f'[{request.user}@{request_ip} [Request: {request.method} {request.path} {request_body}] ' \
                   f'[Response: {response.status_code} {response.reason_phrase} {response_body}]]'
        if response.status_code >= 500:
            logger.error(log_info)
        elif response.status_code >= 400:
            logger.warning(log_info)
        else:
            logger.info(log_info)
        return response


class ResponseMiddleware(MiddlewareMixin):
    """
    自定义响应数据格式
    """

    def process_request(self, request):
        pass

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_exception(self, request, exception):
        pass

    def process_response(self, request, response):
        if isinstance(response, Response) and response.get('content-type') == 'application/json':
            if response.status_code >= 400:
                msg = '请求失败'
                detail = response.data.get('detail')
                code = 40000
                data = {}
            elif response.status_code in [200, 201]:
                msg = '成功'
                detail = ''
                code = 20000
                data = response.data
            else:
                return response
            response.data = {'msg': msg, 'errors': detail, 'code': code, 'data': data}
            response.content = response.rendered_content
        return response


# class OnlineUsersMiddleware(MiddlewareMixin):
#     """
#     在线用户监测, (采用类心跳机制,10分钟内无任何操作则认为该用户已下线)
#     """
#
#     def process_response(self, request, response):
#         if request.user.is_authenticated:
#             from django.core.cache import cache
#             from drf_admin.settings import REDIS_HOST, REDIS_PORT
#
#             last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#             request_ip = get_request_ip(request)
#             cache_key = f'online_user_{request.user.id}_{request_ip}'
#
#             # 检查是否配置了Redis
#             if REDIS_HOST and REDIS_PORT:
#                 # 如果配置了Redis，使用get_redis_connection
#                 conn = get_redis_connection('online_user')
#                 # redis + django orm 实现在线用户监测
#                 if conn.exists(cache_key):
#                     conn.hset(cache_key, 'last_time', last_time)
#                 else:
#                     online_info = {'ip': request_ip, 'browser': get_request_browser(request),
#                                    'os': get_request_os(request), 'last_time': last_time}
#                     conn.hmset(cache_key, online_info)
#                     if not OnlineUsers.objects.filter(user=request.user, ip=request_ip).exists():
#                         OnlineUsers.objects.create(**{'user': request.user, 'ip': request_ip})
#                 # key过期后, 使用redis空间通知, 使用户下线
#                 conn.expire(cache_key, 10 * 60)
#             else:
#                 # 如果没有配置Redis，使用Django缓存API
#                 online_info = cache.get(cache_key)
#                 if online_info:
#                     # 更新最后活跃时间
#                     online_info['last_time'] = last_time
#                     cache.set(cache_key, online_info, 10 * 60)
#                 else:
#                     # 创建新的在线用户记录
#                     online_info = {'ip': request_ip, 'browser': get_request_browser(request),
#                                    'os': get_request_os(request), 'last_time': last_time}
#                     cache.set(cache_key, online_info, 10 * 60)
#                     if not OnlineUsers.objects.filter(user=request.user, ip=request_ip).exists():
#                         OnlineUsers.objects.create(**{'user': request.user, 'ip': request_ip})
#         return response


class IpBlackListMiddleware(MiddlewareMixin):
    """
    IP黑名单校验中间件
    """

    def process_request(self, request):
        request_ip = get_request_ip(request)
        # 在redis中判断IP是否在IP黑名单中/
        from django.core.cache import cache
        from drf_admin.settings import REDIS_HOST, REDIS_PORT

        # 检查是否配置了Redis
        if REDIS_HOST and REDIS_PORT:
            # 如果配置了Redis，使用get_redis_connection
            conn = get_redis_connection('user_info')
            if conn.sismember('ip_black_list', request_ip):
                from django.http import HttpResponse
                return HttpResponse('IP已被拉入黑名单, 请联系管理员', status=status.HTTP_400_BAD_REQUEST)
        else:
            # 如果没有配置Redis，使用Django缓存API
            if cache.get(f'ip_black_list:{request_ip}'):
                from django.http import HttpResponse
                return HttpResponse('IP已被拉入黑名单, 请联系管理员', status=status.HTTP_400_BAD_REQUEST)