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
def role_permissions_changed(sender, instance, **kwargs):
    # 修复：使用查询集方式获取关联用户，并参考permissions.py的缓存机制
    try:
        # 添加调试信息
        logger.info(f"角色权限变更，角色ID: {instance.id}, 角色名称: {instance.name}")
        
        # 使用查询集方式获取关联用户
        users = Users.objects.filter(roles=instance)
        logger.info(f"关联用户数量: {users.count()}")
        
        # 清除相关用户的权限缓存
        for user in users:
            user_info = f"用户ID: {user.id}, 用户名: {user.username}"
            logger.info(f"清除用户权限缓存: {user_info}")
            
            # 检查Redis配置是否存在
            try:
                # 检查settings中是否配置了Redis
                if hasattr(settings, 'REDIS_HOST') and hasattr(settings, 'REDIS_PORT') and settings.REDIS_HOST and settings.REDIS_PORT:
                    # Redis配置存在，使用get_redis_connection清除哈希字段perms
                    logger.info(f"Redis配置存在，清除Redis缓存: {user_info}")
                    conn = get_redis_connection('user_info')
                    conn.hdel(f'user_info_{user.id}', 'perms')
                    logger.info(f"Redis缓存已清除: {user_info}")
                else:
                    # Redis配置不存在，清除Django缓存
                    logger.info(f"Redis配置不存在，使用Django缓存: {user_info}")
                    # 统一使用user_info_前缀的缓存键
                    cache_key = f'user_info_{user.id}_perms'
                    if cache_key in cache:
                        cache.delete(cache_key)
                        logger.info(f"Django缓存已清除: {user_info}")
            except NotImplementedError:
                # Redis后端不支持该功能时，使用Django的cache
                logger.warning(f"Redis connection not available, using Django cache instead for user {user_info}")
                # 统一使用user_info_前缀的缓存键
                cache_key = f'user_info_{user.id}_perms'
                if cache_key in cache:
                    cache.delete(cache_key)
                    logger.info(f"Django缓存已清除: {user_info}")
            except Exception as e:
                logger.error(f"清除权限缓存失败: {str(e)}")
    except Exception as e:
        logger.error(f"处理角色权限变更信号时出错: {str(e)}")


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