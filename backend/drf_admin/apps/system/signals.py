# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver
from django_redis import get_redis_connection
from django.db.models.signals import post_save, m2m_changed

from drf_admin.apps.system.models import Roles, Users

logger = logging.getLogger('info')


# 信号：新用户创建时自动分配默认角色
@receiver(post_save, sender=Users)
def assign_default_role(sender, instance, created, **kwargs):
    if created:
        default_role = Roles.objects.filter(is_default=True).first()
        if default_role:
            instance.roles.add(default_role)


# 信号：角色权限变更时清除关联用户的权限缓存
@receiver(m2m_changed, sender=Roles.permissions.through)
def role_permissions_changed(sender, instance,** kwargs):
    # 使用正确的反向关系名称
    for user in instance.users_set.all():
        try:
            # 检查Redis配置是否存在
            if hasattr(settings, 'REDIS_HOST') and hasattr(settings, 'REDIS_PORT') and settings.REDIS_HOST and settings.REDIS_PORT:
                conn = get_redis_connection('user_info')
                conn.hdel(f'user_info_{user.id}', 'perms')
            else:
                # Redis不可用时，使用Django的cache替代
                cache_key = f'user_info_{user.id}_perms'
                if cache_key in cache:
                    cache.delete(cache_key)
        except NotImplementedError:
            # Redis后端不支持该功能时，使用Django的cache
            logger.warning(f"Redis connection not available, using Django cache instead for user {user.id}")
            cache_key = f'user_info_{user.id}_perms'
            if cache_key in cache:
                cache.delete(cache_key)
        except Exception as e:
            logger.error(f"Error clearing permissions cache for user {user.id}: {str(e)}")


# 信号：用户角色变更时清除权限缓存
@receiver(m2m_changed, sender=Users.roles.through)
def user_roles_changed(sender, instance, **kwargs):
    try:
        # 检查Redis配置是否存在
        if hasattr(settings, 'REDIS_HOST') and hasattr(settings, 'REDIS_PORT') and settings.REDIS_HOST and settings.REDIS_PORT:
            conn = get_redis_connection('user_info')
            conn.hdel(f'user_info_{instance.id}', 'perms')
        else:
            # Redis不可用时，使用Django的cache替代
            cache_key = f'user_info_{instance.id}_perms'
            if cache_key in cache:
                cache.delete(cache_key)
    except NotImplementedError:
        # Redis后端不支持该功能时，使用Django的cache
        logger.warning(f"Redis connection not available, using Django cache instead for user {instance.id}")
        cache_key = f'user_info_{instance.id}_perms'
        if cache_key in cache:
            cache.delete(cache_key)
    except Exception as e:
        logger.error(f"Error clearing permissions cache for user {instance.id}: {str(e)}")
