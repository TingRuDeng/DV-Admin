"""
系统管理模型模块

包含系统管理相关的数据库模型：
- 权限菜单 (Permissions)
- 角色 (Roles)
- 部门 (Departments)
- 字典数据 (DictData, DictItems)
- 通知公告 (Notices, NoticeReads)
- 操作日志 (OperationLog)
"""

from tortoise import fields

from app.db.models.base import BaseModel


class Permissions(BaseModel):
    """
    权限菜单模型

    定义系统中的菜单、按钮、外链等权限资源。
    """

    # 权限类型选项
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
    type = fields.CharField(
        max_length=8, default="", null=True, description="权限类型"
    )
    route_name = fields.CharField(
        max_length=30, null=True, description="路由名"
    )
    route_path = fields.CharField(
        max_length=200, null=True, description="路由路径"
    )
    component = fields.CharField(
        max_length=200, null=True, description="组件路径"
    )
    sort = fields.IntField(default=0, description="排序")
    visible = fields.IntField(default=1, description="是否可见")
    icon = fields.CharField(max_length=30, null=True, description="图标")
    redirect = fields.CharField(max_length=200, null=True, description="重定向")
    perm = fields.CharField(max_length=200, null=True, description="权限标识")
    keep_alive = fields.BooleanField(null=True, description="是否缓存")
    always_show = fields.BooleanField(null=True, description="是否一直显示")
    params = fields.JSONField(default=list, description="参数")
    desc = fields.CharField(max_length=30, null=True, description="权限描述")

    # 自关联：父菜单
    parent = fields.ForeignKeyField(
        "models.Permissions",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE,
        description="父菜单",
    )

    class Meta:
        table = "system_permissions"
        ordering = ["sort"]
        # 数据库索引优化
        indexes = (
            # 单字段索引
            ("type",),
            ("route_name",),
            ("visible",),
            # 联合索引 - 父菜单排序
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
        default=0, description="是否默认角色（新用户自动分配）"
    )
    desc = fields.CharField(max_length=50, default="", description="描述")

    # 多对多关系：权限
    permissions = fields.ManyToManyField(
        "models.Permissions",
        related_name="roles",
        through="system_roles_permissions",
        backward_key="role_id",
        forward_key="permission_id",
        description="权限",
    )

    class Meta:
        table = "system_roles"
        ordering = ["sort"]
        # 数据库索引优化
        indexes = (
            # 单字段索引 - 常用查询字段
            ("code",),
            ("status",),
            ("is_default",),
        )

    def __str__(self) -> str:
        return self.name


class Departments(BaseModel):
    """
    部门模型

    定义组织架构中的部门，支持树形结构。
    """

    name = fields.CharField(max_length=32, description="部门名称")
    status = fields.IntField(default=1, description="状态")
    sort = fields.IntField(default=0, description="排序")

    # 自关联：父部门
    parent = fields.ForeignKeyField(
        "models.Departments",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE,
        description="父部门",
    )

    class Meta:
        table = "system_departments"
        ordering = ["sort"]
        # 数据库索引优化
        indexes = (
            # 单字段索引
            ("status",),
            # 联合索引 - 父部门排序
            ("parent_id", "sort"),
        )

    def __str__(self) -> str:
        return self.name


class Notices(BaseModel):
    """
    通知公告模型
    """

    title = fields.CharField(max_length=200, description="标题")
    content = fields.TextField(description="内容")
    type = fields.IntField(default=0, description="类型")
    level = fields.CharField(max_length=10, default="L", description="级别")
    target_type = fields.IntField(default=1, description="目标类型(1:全体;2:指定)")
    target_user_ids = fields.JSONField(default=list, description="目标用户ID列表")

    publisher_id = fields.IntField(null=True, description="发布人ID")
    publisher_name = fields.CharField(max_length=50, default="", description="发布人名称")

    publish_status = fields.IntField(default=0, description="发布状态(0:未发布;1:已发布;-1:已撤回)")
    publish_time = fields.DatetimeField(null=True, description="发布时间")
    revoke_time = fields.DatetimeField(null=True, description="撤回时间")

    class Meta:
        table = "system_notices"
        ordering = ["-created_at"]
        # 数据库索引优化
        indexes = (
            # 单字段索引
            ("publish_status",),
            ("publisher_id",),
            # 联合索引 - 发布状态+发布时间
            ("publish_status", "publish_time"),
        )


class NoticeReads(BaseModel):
    """
    通知已读记录
    """

    notice = fields.ForeignKeyField(
        "models.Notices",
        related_name="reads",
        on_delete=fields.CASCADE,
        description="通知ID",
    )
    user_id = fields.IntField(description="用户ID")
    read_time = fields.DatetimeField(auto_now_add=True, description="已读时间")

    class Meta:
        table = "system_notice_reads"
        unique_together = ("notice", "user_id")
        # 数据库索引优化
        indexes = (
            # 单字段索引 - 用户查询已读通知
            ("user_id",),
        )


class DictData(BaseModel):
    """
    字典类型模型

    定义字典数据的类型。
    """

    name = fields.CharField(max_length=50, description="字典名称")
    code = fields.CharField(max_length=50, unique=True, description="字典编码")
    status = fields.IntField(default=1, description="状态")
    desc = fields.CharField(max_length=100, default="", description="描述")

    class Meta:
        table = "system_dict_data"
        ordering = ["-created_at"]
        # 数据库索引优化
        indexes = (
            # 单字段索引 - 常用查询字段
            ("code",),
            ("status",),
        )

    def __str__(self) -> str:
        return self.name


class DictItems(BaseModel):
    """
    字典项模型

    定义字典的具体数据项。
    """

    label = fields.CharField(max_length=50, description="标签")
    value = fields.CharField(max_length=50, description="值")
    sort = fields.IntField(default=0, description="排序")
    status = fields.IntField(default=1, description="状态")
    is_default = fields.BooleanField(default=False, description="是否默认")
    remark = fields.CharField(max_length=100, default="", description="备注")

    # 外键：字典类型
    dict_data = fields.ForeignKeyField(
        "models.DictData",
        related_name="items",
        on_delete=fields.CASCADE,
        description="字典类型",
    )

    class Meta:
        table = "system_dict_items"
        ordering = ["sort"]
        # 数据库索引优化
        indexes = (
            # 单字段索引
            ("status",),
            # 联合索引 - 字典类型+排序
            ("dict_data_id", "sort"),
            # 联合索引 - 字典类型+状态
            ("dict_data_id", "status"),
        )

    def __str__(self) -> str:
        return self.label


class OperationLog(BaseModel):
    """
    操作日志模型

    记录用户的操作行为，包括请求信息、响应状态、执行时间等。
    """

    # 用户信息
    user_id = fields.IntField(null=True, description="用户ID")
    username = fields.CharField(max_length=150, default="", description="用户名")
    name = fields.CharField(max_length=50, default="", description="用户姓名")

    # 操作信息
    operation = fields.CharField(max_length=100, default="", description="操作描述")
    method = fields.CharField(max_length=10, default="", description="请求方法")
    path = fields.CharField(max_length=500, default="", description="请求路径")
    query_params = fields.TextField(default="", description="查询参数")

    # 请求/响应信息
    request_body = fields.TextField(default="", description="请求体")
    response_status = fields.IntField(default=0, description="响应状态码")
    response_body = fields.TextField(default="", description="响应体")

    # 执行信息
    ip = fields.CharField(max_length=50, default="", description="IP地址")
    browser = fields.CharField(max_length=100, default="", description="浏览器")
    os = fields.CharField(max_length=100, default="", description="操作系统")
    execution_time = fields.IntField(default=0, description="执行时间(毫秒)")

    # 状态
    status = fields.IntField(default=1, description="状态(1:成功;0:失败)")
    error_msg = fields.TextField(default="", description="错误信息")

    class Meta:
        table = "system_operation_log"
        ordering = ["-created_at"]
        # 数据库索引优化
        indexes = (
            # 单字段索引 - 常用查询字段
            ("user_id",),
            ("username",),
            ("status",),
            ("method",),
            # 联合索引 - 用户+时间
            ("user_id", "created_at"),
            # 联合索引 - 状态+时间
            ("status", "created_at"),
        )

    def __str__(self) -> str:
        return f"{self.username} - {self.operation}"
