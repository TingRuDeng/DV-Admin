"""
系统权限与角色模型
"""

from __future__ import annotations

from typing import Any

from tortoise import fields

from app.db.models.base import BaseModel


class Permissions(BaseModel):
    """
    权限菜单模型

    定义系统中的菜单、按钮、外链等权限资源。
    """

    TYPE_CATALOG = "CATALOG"  # 根目录
    TYPE_MENU = "MENU"  # 菜单
    TYPE_BUTTON = "BUTTON"  # 按钮
    TYPE_EXT_LINK = "EXTLINK"  # 外链

    TYPE_CHOICES = [
        (TYPE_CATALOG, "根目录"),
        (TYPE_MENU, "菜单"),
        (TYPE_BUTTON, "按钮"),
        (TYPE_EXT_LINK, "外链"),
    ]

    name = fields.CharField(max_length=30, description="名称")
    type = fields.CharField(max_length=8, default="", description="权限类型")
    route_name = fields.CharField(max_length=30, null=True, description="路由名")
    route_path = fields.CharField(max_length=200, null=True, description="路由路径")
    component = fields.CharField(max_length=200, null=True, description="组件路径")
    sort = fields.IntField(default=0, description="排序")
    visible = fields.IntField(default=1, description="是否可见")
    icon = fields.CharField(max_length=30, null=True, description="图标")
    redirect = fields.CharField(max_length=200, null=True, description="重定向")
    perm = fields.CharField(max_length=200, null=True, description="权限标识")
    keep_alive = fields.BooleanField(null=True, description="是否缓存")
    always_show = fields.BooleanField(null=True, description="是否一直显示")
    params: fields.Field[list[dict[str, Any]]] = fields.JSONField(
        default=list,
        description="参数",
    )
    desc = fields.CharField(max_length=30, null=True, description="权限描述")

    parent: fields.ForeignKeyNullableRelation[Permissions] = fields.ForeignKeyField(
        "models.Permissions",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE,
        description="父菜单",
    )
    parent_id: int | None

    class Meta:
        table = "system_permissions"
        ordering = ["sort"]
        indexes = (
            ("type",),
            ("route_name",),
            ("visible",),
            ("parent_id", "sort"),
        )

    def __str__(self) -> str:
        return self.name


class Roles(BaseModel):
    """
    角色模型

    定义系统中的角色，角色可以关联多个权限。
    """

    name = fields.CharField(max_length=32, unique=True, description="角色名称")
    code = fields.CharField(max_length=32, null=True, description="角色编码")
    status = fields.IntField(default=1, description="状态")
    sort = fields.IntField(default=0, description="排序")
    is_default = fields.IntField(
        default=0,
        description="是否默认角色（新用户自动分配）",
    )
    desc = fields.CharField(max_length=50, default="", description="描述")

    permissions: fields.ManyToManyRelation[Permissions] = fields.ManyToManyField(
        "models.Permissions",
        related_name="roles",
        through="system_roles_to_system_permissions",
        backward_key="roles_id",
        forward_key="permissions_id",
        description="权限",
    )

    class Meta:
        table = "system_roles"
        ordering = ["sort"]
        indexes = (
            ("code",),
            ("status",),
            ("is_default",),
        )

    def __str__(self) -> str:
        return self.name
