import re
import json
import logging

from django.conf import settings
from django.core.cache import cache
from django_redis import get_redis_connection
from rest_framework.permissions import BasePermission

logger = logging.getLogger('info')


class RBACPermission(BasePermission):
    """
=    自定义视图/接口级权限校验的 RBAC 类，后续根据需求可以对数据级别进行权限校验
    - 支持 ViewSet（通过 action 映射权限）和 APIView（通过 HTTP 方法映射权限）
    - 视图需定义 required_permissions 字典，键为 action 或 HTTP 方法
    """

    @staticmethod
    def _get_operation(view, request):
        """获取操作标识（适配 ViewSet 和 APIView），增强兼容性"""
        # 尝试从ViewSet的action获取
        if hasattr(view, 'action') and view.action:
            return view.action  # ViewSet 使用 action

        # 如果action为空，检查请求方法
        return request.method.lower()  # APIView 使用 HTTP 方法

    @staticmethod
    def get_user_permissions(user):
        """获取用户拥有的所有权限（带缓存）"""
        conn = None
        user_perms = set()
        # 统一使用user_info_前缀的缓存键
        cache_key = f'user_info_{user.id}_perms'
        # 检查Redis配置是否存在
        if hasattr(settings, 'REDIS_HOST') and hasattr(settings, 'REDIS_PORT') and settings.REDIS_HOST and settings.REDIS_PORT:
            try:
                conn = get_redis_connection('user_info')
                if conn.exists(f'user_info_{user.id}'):
                    cached_perms = conn.hget(f'user_info_{user.id}', 'perms')
                    if cached_perms is not None:
                        return json.loads(cached_perms.decode())
            except Exception as e:
                logger.error(f"Redis connection error: {str(e)}")
        else:
            # 尝试从Django缓存获取
            cached_perms = cache.get(cache_key)
            if cached_perms:
                return cached_perms

        # 从数据库查询用户权限（通过角色关联）
        for role in user.roles.all():
            user_perms.update(role.permissions.values_list("perm", flat=True))

        # 转换为列表格式
        user_perms_list = list(user_perms)

        # 根据Redis可用性选择缓存方式
        if hasattr(settings, 'REDIS_HOST') and hasattr(settings, 'REDIS_PORT') and settings.REDIS_HOST and settings.REDIS_PORT:
            try:
                # 缓存到Redis，1小时
                conn.hset(f'user_info_{user.id}', 'perms', json.dumps(user_perms_list))
            except Exception as e:
                logger.error(f"Redis cache error: {str(e)}")
        else:
            # 缓存到Django本地缓存，1小时
            cache.set(cache_key, user_perms_list, 60 * 60)

        return user_perms_list

    def has_permission(self, request, view):
        request_url = request.path
        # 如果请求url在白名单，放行
        for safe_url in settings.WHITE_LIST:
            if re.match(settings.REGEX_URL.format(url=safe_url), request_url):
                return True

        # RBAC权限验证
        # 获取当前操作标识（ViewSet 用 action，APIView 用 HTTP 方法）
        operation = self._get_operation(view, request)
        # 从required_permissions获取权限要求
        required_perms = []
        if hasattr(view, 'required_permissions'):
            required_perms = view.required_permissions.get(operation, [])
        if not required_perms:
            # 未指定权限的操作默认拒绝
            return False

        # 检查用户是否拥有所有必需权限
        user_perms = self.get_user_permissions(request.user)
        return all(perm in user_perms for perm in required_perms)