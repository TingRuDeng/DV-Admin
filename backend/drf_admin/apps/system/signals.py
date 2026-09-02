# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver
from django_redis import get_redis_connection

from drf_admin.apps.system.models import Permissions, Roles, Users

logger = logging.getLogger('error')


def clear_user_permission_cache(user_id):
    """清除单个用户的 RBAC 权限缓存，兼容 Redis 与本地缓存后端。"""
    try:
        if settings.REDIS_HOST and settings.REDIS_PORT:
            conn = get_redis_connection('user_info')
            conn.hdel(f'user_info_{user_id}', 'perms')
        else:
            cache.delete(f'user_info_{user_id}_perms')
    except NotImplementedError:
        cache.delete(f'user_info_{user_id}_perms')
    except Exception as e:
        logger.error(f"清除用户 {user_id} 权限缓存失败: {str(e)}")


@receiver(post_save, sender=Users)
def assign_default_role(sender, instance, created, **kwargs):
    if created:
        default_role = Roles.objects.filter(is_default=True).first()
        if default_role:
            instance.roles.add(default_role)


@receiver(m2m_changed, sender=Roles.permissions.through)
def role_permissions_changed(sender, instance, **kwargs):
    try:
        user_ids = Users.objects.filter(roles=instance).values_list('id', flat=True)
        for user_id in user_ids:
            clear_user_permission_cache(user_id)
    except Exception as e:
        logger.error(f"处理角色权限变更信号时出错: {str(e)}")


@receiver(m2m_changed, sender=Users.roles.through)
def user_roles_changed(sender, instance, **kwargs):
    clear_user_permission_cache(instance.id)


@receiver(pre_delete, sender=Permissions)
def permission_deleting(sender, instance, **kwargs):
    """权限对象删除前清除关联用户缓存，避免级联删除绕过 m2m_changed。"""
    try:
        user_ids = Users.objects.filter(roles__permissions=instance).values_list('id', flat=True).distinct()
        for user_id in user_ids:
            clear_user_permission_cache(user_id)
    except Exception as e:
        logger.error(f"处理权限删除信号时出错: {str(e)}")
