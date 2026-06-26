"""
认证授权模型模块

包含用户认证相关的数据库模型：
- 用户 (Users)
"""

from __future__ import annotations

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
    dept: fields.ForeignKeyNullableRelation[Departments] = fields.ForeignKeyField(
        "models.Departments",
        related_name="users",
        null=True,
        on_delete=fields.SET_NULL,
        description="直属部门",
    )
    dept_id: int | None

    # 多对多关系：角色
    roles: fields.ManyToManyRelation[Roles] = fields.ManyToManyField(
        "models.Roles",
        related_name="users",
        through="system_users_to_system_roles",
        backward_key="users_id",
        forward_key="roles_id",
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
        from app.db.models.oauth_user_access import get_user_permissions

        return await get_user_permissions(self)

    async def get_menus(self):
        """
        获取用户菜单（带缓存）

        Returns:
            菜单列表（树形结构）
        """
        from app.db.models.oauth_user_access import get_user_menus

        return await get_user_menus(self)

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
