# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver
from django_redis import get_redis_connection
from django.db.models.signals import post_save, m2m_changed

from drf_admin.apps.system.models import Roles, Users

logger = logging.getLogger('error')


@receiver(post_save, sender=Users)
def assign_default_role(sender, instance, created, **kwargs):
    if created:
        default_role = Roles.objects.filter(is_default=True).first()
        if default_role:
            instance.roles.add(default_role)


@receiver(m2m_changed, sender=Roles.permissions.through)
def role_permissions_changed(sender, instance, **kwargs):
    try:
        users = Users.objects.filter(roles=instance)
        for user in users:
            try:
                if settings.REDIS_HOST and settings.REDIS_PORT:
                    conn = get_redis_connection('user_info')
                    conn.hdel(f'user_info_{user.id}', 'perms')
                else:
                    cache_key = f'user_info_{user.id}_perms'
                    cache.delete(cache_key)
            except NotImplementedError:
                cache_key = f'user_info_{user.id}_perms'
                cache.delete(cache_key)
            except Exception as e:
                logger.error(f"清除权限缓存失败: {str(e)}")
    except Exception as e:
        logger.error(f"处理角色权限变更信号时出错: {str(e)}")


@receiver(m2m_changed, sender=Users.roles.through)
def user_roles_changed(sender, instance, **kwargs):
    try:
        if settings.REDIS_HOST and settings.REDIS_PORT:
            conn = get_redis_connection('user_info')
            conn.hdel(f'user_info_{instance.id}', 'perms')
        else:
            cache_key = f'user_info_{instance.id}_perms'
            cache.delete(cache_key)
    except NotImplementedError:
        cache_key = f'user_info_{instance.id}_perms'
        cache.delete(cache_key)
    except Exception as e:
        logger.error(f"清除用户 {instance.id} 权限缓存失败: {str(e)}")
