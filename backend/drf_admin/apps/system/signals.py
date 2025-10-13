# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver
from django_redis import get_redis_connection
from django.db.models.signals import post_save, m2m_changed

from drf_admin.apps.system.models import Roles, Users


# 信号：新用户创建时自动分配默认角色
@receiver(post_save, sender=Users)
def assign_default_role(sender, instance, created, **kwargs):
    if created:
        default_role = Roles.objects.filter(is_default=True).first()
        if default_role:
            instance.roles.add(default_role)


# 信号：角色权限变更时清除关联用户的权限缓存


@receiver(m2m_changed, sender=Roles.permissions.through)
def role_permissions_changed(sender, instance, **kwargs):
    # 修复：使用查询集方式获取关联用户，并参考permissions.py的缓存机制
    try:
        # 使用查询集方式获取关联用户
        users = Users.objects.filter(roles=instance)

        # 清除相关用户的权限缓存
        for user in users:
            try:
                if settings.REDIS_HOST and settings.REDIS_PORT:
                    # Redis配置存在，使用get_redis_connection清除哈希字段perms
                    conn = get_redis_connection('user_info')
                    conn.hdel(f'user_info_{user.id}', 'perms')
                else:
                    # Redis配置不存在，清除Django缓存
                    cache_key = f'user_info_{user.id}_perms'
                    if cache_key in cache:
                        cache.delete(cache_key)
            except NotImplementedError:
                # Redis后端不支持该功能时，使用Django的cache
                # 统一使用user_info_前缀的缓存键
                cache_key = f'user_info_{user.id}_perms'
                if cache_key in cache:
                    cache.delete(cache_key)
            except Exception as e:
                print(f"清除权限缓存失败: {str(e)}")
    except Exception as e:
        print(f"处理角色权限变更信号时出错: {str(e)}")


# 信号：用户角色变更时清除权限缓存
@receiver(m2m_changed, sender=Users.roles.through)
def user_roles_changed(sender, instance, **kwargs):
    try:
        if settings.REDIS_HOST and settings.REDIS_PORT:
            conn = get_redis_connection('user_info')
            conn.hdel(f'user_info_{instance.id}', 'perms')
        else:
            # Redis不可用时，使用Django的cache替代
            cache_key = f'user_info_{instance.id}_perms'
            if cache_key in cache:
                cache.delete(cache_key)
    except NotImplementedError:
        # Redis后端不支持该功能时，使用Django的cache
        cache_key = f'user_info_{instance.id}_perms'
        if cache_key in cache:
            cache.delete(cache_key)
    except Exception as e:
        print(f"Error clearing permissions cache for user {instance.id}: {str(e)}")
