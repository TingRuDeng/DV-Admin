# -*- coding: utf-8 -*-
"""
认证授权模型模块

包含用户认证相关的数据库模型：
- 用户 (Users)
"""

from tortoise import fields

from app.db.models.base import BaseModel
from app.db.models.system import Departments, Roles


class Users(BaseModel):
    """
    用户模型

    定义系统中的用户，继承自 AbstractUser 的功能。
    """

    # 性别选项
    GENDER_UNKNOWN = 0
    GENDER_MALE = 1
    GENDER_FEMALE = 2

    GENDER_CHOICES = [
        (GENDER_UNKNOWN, "保密"),
        (GENDER_MALE, "男"),
        (GENDER_FEMALE, "女"),
    ]

    # 基础信息
    username = fields.CharField(
        max_length=150, unique=True, description="用户名"
    )
    password = fields.CharField(max_length=128, description="密码")
    name = fields.CharField(
        max_length=20, default="", description="真实姓名"
    )
    email = fields.CharField(
        max_length=254, null=True, default=None, description="邮箱"
    )
    mobile = fields.CharField(
        max_length=11, unique=True, null=True, default=None, description="手机号码"
    )
    avatar = fields.CharField(
        max_length=255, default="avatar/default.png", description="头像"
    )
    gender = fields.IntField(
        default=GENDER_UNKNOWN, description="性别"
    )
    is_active = fields.IntField(default=1, description="是否激活")
    is_superuser = fields.BooleanField(default=False, description="是否超级用户")
    is_staff = fields.BooleanField(default=False, description="是否 staff")

    # 外键关系
    dept = fields.ForeignKeyField(
        "models.Departments",
        related_name="users",
        null=True,
        on_delete=fields.SET_NULL,
        description="直属部门",
    )

    # 多对多关系：角色
    roles = fields.ManyToManyField(
        "models.Roles",
        related_name="users",
        through="system_users_roles",
        backward_key="user_id",
        forward_key="role_id",
        description="角色",
    )

    # Django 兼容字段
    last_login = fields.DatetimeField(null=True, description="最后登录时间")
    first_name = fields.CharField(
        max_length=30, default="", description="名"
    )
    last_name = fields.CharField(
        max_length=30, default="", description="姓"
    )
    date_joined = fields.DatetimeField(
        auto_now_add=True, description="加入时间"
    )

    class Meta:
        table = "system_users"
        ordering = ["id"]
        # 数据库索引优化
        indexes = (
            # 单字段索引 - 常用查询字段
            ("username",),
            ("mobile",),
            ("email",),
            ("is_active",),
            # 联合索引 - 部门+状态查询
            ("dept_id", "is_active"),
        )

    def __str__(self) -> str:
        return self.username

    @property
    def full_name(self) -> str:
        """获取全名"""
        return f"{self.first_name}{self.last_name}" or self.name or self.username

    @property
    def is_authenticated(self) -> bool:
        """是否已认证"""
        return True

    async def get_permissions(self) -> list:
        """
        获取用户所有权限标识（带缓存）

        Returns:
            权限标识列表
        """
        from app.core.cache import cache_service, CacheKeys

        # 超级用户返回空列表（拥有所有权限）
        if self.is_superuser:
            return []

        # 尝试从缓存获取
        cache_key = CacheKeys.format_key(CacheKeys.USER_PERMISSIONS, user_id=self.id)
        cached = await cache_service.get(cache_key)
        if cached is not None:
            return cached

        permissions = set()

        # 获取所有角色的权限 - 使用 prefetch_related 优化 N+1 查询
        await self.fetch_related("roles")
        role_ids = [role.id for role in self.roles]

        if role_ids:
            from app.db.models.system import Roles
            roles_with_perms = await Roles.filter(id__in=role_ids).prefetch_related("permissions")
            for role in roles_with_perms:
                for perm in role.permissions:
                    if perm.perm:
                        permissions.add(perm.perm)

        result = list(permissions)
        # 缓存 10 分钟
        await cache_service.set(cache_key, result, ttl=600)
        return result

    async def get_menus(self):
        """
        获取用户菜单（带缓存）

        Returns:
            菜单列表（树形结构）
        """
        from app.core.cache import cache_service, CacheKeys
        from app.db.models.system import Permissions

        # 尝试从缓存获取
        cache_key = CacheKeys.format_key(CacheKeys.USER_MENUS, user_id=self.id)
        cached = await cache_service.get(cache_key)
        if cached is not None:
            return cached

        # 获取用户角色的所有菜单权限 - 使用 prefetch_related 优化
        await self.fetch_related("roles")
        role_ids = [role.id for role in self.roles]

        menu_ids = set()
        if role_ids:
            roles_with_perms = await Roles.filter(id__in=role_ids).prefetch_related("permissions")
            for role in roles_with_perms:
                for perm in role.permissions:
                    if perm.type in [
                        Permissions.TYPE_CATALOG,
                        Permissions.TYPE_MENU,
                        Permissions.TYPE_EXT_LINK,
                    ]:
                        menu_ids.add(perm.id)

        # 查询菜单
        menus = await Permissions.filter(
            id__in=menu_ids, visible=1
        ).order_by("sort")

        # 将菜单转换为树形结构
        menu_dict = {}
        menu_list = []

        # 先将所有菜单放入字典
        for menu in menus:
            # 先创建基础菜单字典
            menu_item = {
                'path': menu.route_path,
                'component': menu.component if menu.component else 'Layout',
                'name': menu.route_name if menu.route_name else menu.route_path,
                'meta': {
                    'title': menu.name,
                    'icon': menu.icon if menu.icon else '',
                    'hidden': False if menu.visible else True,
                    'alwaysShow': False if menu.always_show is None else menu.always_show,
                    'params': menu.params if menu.params else [],
                    'keepAlive': False if menu.keep_alive is None else menu.keep_alive,
                },
                'children': []
            }

            # 只有当redirect有值时才添加该字段
            if menu.redirect:
                menu_item['redirect'] = menu.redirect

            menu_dict[menu.id] = {"item": menu_item, "parent_id": menu.parent_id}

        # 构建树形结构
        for menu in menus:
            if menu.parent_id is None:
                # 根菜单直接加入列表
                menu_list.append(menu_dict[menu.id]["item"])
            else:
                # 子菜单添加到父菜单的children中
                if menu.parent_id in menu_dict:
                    menu_dict[menu.parent_id]["item"]['children'].append(menu_dict[menu.id]["item"])

        # 移除空的children字段
        def remove_empty_children(menu_items):
            for item in menu_items:
                if 'children' in item and len(item['children']) == 0:
                    del item['children']
                elif 'children' in item and len(item['children']) > 0:
                    remove_empty_children(item['children'])

        remove_empty_children(menu_list)

        # 缓存 10 分钟
        await cache_service.set(cache_key, menu_list, ttl=600)
        return menu_list

    async def has_perm(self, perm_code: str) -> bool:
        """
        检查用户是否有指定权限

        Args:
            perm_code: 权限标识

        Returns:
            是否有权限
        """
        if self.is_superuser:
            return True

        permissions = await self.get_permissions()
        return perm_code in permissions

    async def has_role(self, role_code: str) -> bool:
        """
        检查用户是否有指定角色

        Args:
            role_code: 角色编码

        Returns:
            是否有角色
        """
        await self.fetch_related("roles")
        for role in self.roles:
            if role.code == role_code:
                return True
        return False
