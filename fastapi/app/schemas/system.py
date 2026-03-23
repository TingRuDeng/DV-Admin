"""
系统管理 Schema 模块

定义系统管理相关的 Pydantic 模型。
"""

from datetime import datetime
from typing import Any, List

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampSchema

# ==================== 用户管理 ====================

class UserBase(BaseSchema):
    """用户基础信息"""

    username: str = Field(description="用户名")
    name: str | None = Field(default=None, description="真实姓名")
    email: str | None = Field(default=None, description="邮箱")
    mobile: str | None = Field(default=None, description="手机号")
    gender: int = Field(default=0, description="性别")
    is_active: int = Field(default=1, description="是否激活")
    dept_id: int | None = Field(default=None, description="部门ID")


class UserCreate(UserBase):
    """创建用户请求"""

    password: str | None = Field(default=None, description="密码")
    role_ids: list[int] = Field(default=[], alias="roles", description="角色ID列表")
    avatar: str | None = Field(default="avatar/default.png", description="头像")


class UserUpdate(BaseSchema):
    """更新用户请求"""

    name: str | None = Field(default=None, description="真实姓名")
    email: str | None = Field(default=None, description="邮箱")
    mobile: str | None = Field(default=None, description="手机号")
    gender: int | None = Field(default=None, description="性别")
    is_active: int | None = Field(default=None, description="是否激活")
    dept_id: int | None = Field(default=None, description="部门ID")
    role_ids: list[int] | None = Field(default=None, alias="roles", description="角色ID列表")
    avatar: str | None = Field(default=None, description="头像")


class UserPartialUpdate(BaseSchema):
    """局部更新用户（用于激活/禁用）"""

    is_active: int = Field(description="是否激活")


class UserOut(TimestampSchema):
    """用户响应数据"""

    username: str = Field(description="用户名")
    name: str | None = Field(default=None, description="真实姓名")
    email: str | None = Field(default=None, description="邮箱")
    mobile: str | None = Field(default=None, description="手机号")
    avatar: str = Field(default="avatar/default.png", description="头像")
    gender: int = Field(default=0, description="性别")
    is_active: int = Field(default=1, description="是否激活")
    dept_id: int | None = Field(default=None, description="部门ID")
    dept_name: str | None = Field(default=None, description="部门名称")
    role_names: str | None = Field(default=None, description="角色名称")

    @field_validator("role_names", mode="before")
    @classmethod
    def validate_role_names(cls, v):
        """验证角色名称"""
        if isinstance(v, list):
            return ",".join(v)
        return v


class UserFormOut(UserOut):
    """用户表单响应数据（用于编辑回填）"""

    roles: list[int] = Field(default=[], description="角色ID列表")


class UserPageQuery(BaseSchema):
    """用户分页查询"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    search: str | None = Field(default=None, description="搜索关键词")
    is_active: int | None = Field(default=None, description="状态")
    dept_id: int | None = Field(default=None, description="部门ID")


# ==================== 角色管理 ====================

class RoleBase(BaseSchema):
    """角色基础信息"""

    name: str = Field(description="角色名称")
    code: str | None = Field(default=None, description="角色编码")
    status: int = Field(default=1, description="状态")
    sort: int = Field(default=0, description="排序")
    is_default: int = Field(default=0, description="是否默认")
    desc: str | None = Field(default=None, description="描述")


class RoleCreate(RoleBase):
    """创建角色请求"""

    permission_ids: list[int] = Field(default=[], description="权限ID列表")


class RoleUpdate(BaseSchema):
    """更新角色请求"""

    name: str | None = Field(default=None, description="角色名称")
    code: str | None = Field(default=None, description="角色编码")
    status: int | None = Field(default=None, description="状态")
    sort: int | None = Field(default=None, description="排序")
    is_default: int | None = Field(default=None, description="是否默认")
    desc: str | None = Field(default=None, description="描述")
    permission_ids: list[int] | None = Field(default=None, description="权限ID列表")


class RoleOut(TimestampSchema):
    """角色响应数据"""

    name: str = Field(description="角色名称")
    code: str | None = Field(default=None, description="角色编码")
    status: int = Field(default=1, description="状态")
    sort: int = Field(default=0, description="排序")
    is_default: int = Field(default=0, description="是否默认")
    desc: str | None = Field(default=None, description="描述")


class RoleWithPermissions(RoleOut):
    """带权限的角色数据"""

    permissions: list[int] = Field(default=[], description="权限ID列表")


# ==================== 通知公告 ====================

class NoticeBase(BaseSchema):
    """通知公告基础信息"""

    title: str = Field(description="标题")
    content: str = Field(description="内容")
    type: int = Field(default=0, description="类型")
    level: str = Field(default="L", description="级别")
    target_type: int = Field(default=1, description="目标类型(1:全体;2:指定)")
    target_user_ids: list[int] = Field(default=[], description="目标用户ID列表")


class NoticeCreate(NoticeBase):
    """创建通知公告请求"""
    pass


class NoticeUpdate(BaseSchema):
    """更新通知公告请求"""

    title: str | None = Field(default=None, description="标题")
    content: str | None = Field(default=None, description="内容")
    type: int | None = Field(default=None, description="类型")
    level: str | None = Field(default=None, description="级别")
    target_type: int | None = Field(default=None, description="目标类型(1:全体;2:指定)")
    target_user_ids: list[int] | None = Field(default=None, description="目标用户ID列表")


class NoticeFormOut(BaseSchema):
    """通知公告表单数据"""

    id: int = Field(description="通知ID")
    title: str = Field(description="标题")
    content: str = Field(description="内容")
    type: int = Field(default=0, description="类型")
    level: str = Field(default="L", description="级别")
    target_type: int = Field(default=1, description="目标类型(1:全体;2:指定)")
    target_user_ids: list[int] = Field(default=[], description="目标用户ID列表")


class NoticePageOut(BaseSchema):
    """通知公告分页数据"""

    model_config = {"alias_generator": None}

    id: int = Field(description="通知ID")
    title: str = Field(description="标题")
    content: str | None = Field(default=None, description="内容")
    type: int = Field(default=0, description="类型")
    level: str = Field(default="L", description="级别")
    target_type: int = Field(default=1, description="目标类型(1:全体;2:指定)")
    publisher_id: int | None = Field(default=None, description="发布人ID")
    publisher_name: str = Field(default="", description="发布人名称")
    publish_status: int = Field(default=0, description="发布状态")
    create_time: datetime | None = Field(default=None, description="创建时间")
    publish_time: datetime | None = Field(default=None, description="发布时间")
    revoke_time: datetime | None = Field(default=None, description="撤回时间")


class NoticeMyPageOut(NoticePageOut):
    """我的通知分页数据"""

    is_read: int = Field(default=0, description="是否已读(1:是;0:否)")


class NoticeDetailOut(BaseSchema):
    """通知公告详情"""

    id: int = Field(description="通知ID")
    title: str = Field(description="标题")
    content: str = Field(description="内容")
    type: int = Field(default=0, description="类型")
    level: str = Field(default="L", description="级别")
    publisher_name: str = Field(default="", description="发布人名称")
    publish_time: datetime | None = Field(default=None, description="发布时间")
    publish_status: int = Field(default=0, description="发布状态")


class NoticeAdminPageResult(BaseSchema):
    """通知公告分页结果（后台列表）"""

    list: List[NoticePageOut] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数")

    @property
    def results(self) -> List[NoticePageOut]:
        return self.list

    @property
    def count(self) -> int:
        return self.total


class NoticeMyPageResult(BaseSchema):
    """通知公告分页结果（我的通知）"""

    list: List[NoticeMyPageOut] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数")


    @property
    def results(self) -> List[NoticeMyPageOut]:
        return self.list

    @property
    def count(self) -> int:
        return self.total


# ==================== 菜单/权限管理 ====================

class MenuBase(BaseSchema):
    """菜单基础信息"""

    name: str = Field(description="名称")
    type: str = Field(default="MENU", description="权限类型")
    route_name: str | None = Field(default=None, description="路由名")
    route_path: str | None = Field(default=None, description="路由路径")
    component: str | None = Field(default=None, description="组件路径")
    sort: int = Field(default=0, description="排序")
    visible: int = Field(default=1, description="是否可见")
    icon: str | None = Field(default=None, description="图标")
    redirect: str | None = Field(default=None, description="重定向")
    perm: str | None = Field(default=None, description="权限标识")
    keep_alive: bool | None = Field(default=None, description="是否缓存")
    always_show: bool | None = Field(default=None, description="是否一直显示")
    params: list[dict[str, Any]] = Field(default=[], description="参数")
    desc: str | None = Field(default=None, description="描述")
    parent_id: int | None = Field(default=None, description="父菜单ID")


class MenuCreate(MenuBase):
    """创建菜单请求"""
    pass


class MenuUpdate(BaseSchema):
    """更新菜单请求"""

    name: str | None = Field(default=None, description="名称")
    type: str | None = Field(default=None, description="权限类型")
    route_name: str | None = Field(default=None, description="路由名")
    route_path: str | None = Field(default=None, description="路由路径")
    component: str | None = Field(default=None, description="组件路径")
    sort: int | None = Field(default=None, description="排序")
    visible: int | None = Field(default=None, description="是否可见")
    icon: str | None = Field(default=None, description="图标")
    redirect: str | None = Field(default=None, description="重定向")
    perm: str | None = Field(default=None, description="权限标识")
    keep_alive: bool | None = Field(default=None, description="是否缓存")
    always_show: bool | None = Field(default=None, description="是否一直显示")
    params: list[dict[str, Any]] | None = Field(default=None, description="参数")
    desc: str | None = Field(default=None, description="描述")
    parent_id: int | None = Field(default=None, description="父菜单ID")


class MenuOut(TimestampSchema):
    """菜单响应数据"""

    name: str = Field(description="名称")
    type: str = Field(description="权限类型")
    route_name: str | None = Field(default=None, description="路由名")
    route_path: str | None = Field(default=None, description="路由路径")
    component: str | None = Field(default=None, description="组件路径")
    sort: int = Field(default=0, description="排序")
    visible: int = Field(default=1, description="是否可见")
    icon: str | None = Field(default=None, description="图标")
    redirect: str | None = Field(default=None, description="重定向")
    perm: str | None = Field(default=None, description="权限标识")
    keep_alive: bool | None = Field(default=None, description="是否缓存")
    always_show: bool | None = Field(default=None, description="是否一直显示")
    params: list[dict[str, Any]] = Field(default=[], description="参数")
    desc: str | None = Field(default=None, description="描述")
    parent_id: int | None = Field(default=None, description="父菜单ID")


class MenuTree(MenuOut):
    """菜单树形结构"""

    children: list["MenuTree"] = Field(default=[], description="子菜单")


# ==================== 部门管理 ====================

class DeptBase(BaseSchema):
    """部门基础信息"""

    name: str = Field(description="部门名称")
    status: int = Field(default=1, description="状态")
    sort: int = Field(default=0, description="排序")
    parent_id: int | None = Field(default=None, description="父部门ID")


class DeptCreate(DeptBase):
    """创建部门请求"""
    pass


class DeptUpdate(BaseSchema):
    """更新部门请求"""

    name: str | None = Field(default=None, description="部门名称")
    status: int | None = Field(default=None, description="状态")
    sort: int | None = Field(default=None, description="排序")
    parent_id: int | None = Field(default=None, description="父部门ID")


class DeptOut(TimestampSchema):
    """部门响应数据"""

    name: str = Field(description="部门名称")
    status: int = Field(default=1, description="状态")
    sort: int = Field(default=0, description="排序")
    parent_id: int | None = Field(default=None, description="父部门ID")


class DeptTree(DeptOut):
    """部门树形结构"""

    label: str | None = Field(default=None, description="部门名称(兼容前端)")
    children: list["DeptTree"] = Field(default=[], description="子部门")


# ==================== 字典管理 ====================

class DictDataBase(BaseSchema):
    """字典类型基础信息"""

    name: str = Field(description="字典名称")
    code: str = Field(description="字典编码")
    status: int = Field(default=1, description="状态")
    desc: str | None = Field(default=None, description="描述")


class DictDataCreate(DictDataBase):
    """创建字典类型请求"""
    pass


class DictDataUpdate(BaseSchema):
    """更新字典类型请求"""

    name: str | None = Field(default=None, description="字典名称")
    code: str | None = Field(default=None, description="字典编码")
    status: int | None = Field(default=None, description="状态")
    desc: str | None = Field(default=None, description="描述")


class DictDataOut(TimestampSchema):
    """字典类型响应数据"""

    name: str = Field(description="字典名称")
    code: str = Field(description="字典编码")
    status: int = Field(default=1, description="状态")
    desc: str | None = Field(default=None, description="描述")


class DictItemBase(BaseSchema):
    """字典项基础信息"""

    label: str = Field(description="标签")
    value: str = Field(description="值")
    sort: int = Field(default=0, description="排序")
    status: int = Field(default=1, description="状态")
    is_default: bool = Field(default=False, description="是否默认")
    remark: str | None = Field(default=None, description="备注")


class DictItemCreate(DictItemBase):
    """创建字典项请求"""

    dict_data_id: int = Field(description="字典类型ID")


class DictItemUpdate(BaseSchema):
    """更新字典项请求"""

    label: str | None = Field(default=None, description="标签")
    value: str | None = Field(default=None, description="值")
    sort: int | None = Field(default=None, description="排序")
    status: int | None = Field(default=None, description="状态")
    is_default: bool | None = Field(default=None, description="是否默认")
    remark: str | None = Field(default=None, description="备注")


class DictItemOut(TimestampSchema):
    """字典项响应数据"""

    label: str = Field(description="标签")
    value: str = Field(description="值")
    sort: int = Field(default=0, description="排序")
    status: int = Field(default=1, description="状态")
    is_default: bool = Field(default=False, description="是否默认")
    remark: str | None = Field(default=None, description="备注")
    dict_data_id: int = Field(description="字典类型ID")


class DictWithItems(DictDataOut):
    """带字典项的字典类型"""

    items: list[DictItemOut] = Field(default=[], description="字典项列表")


class BulkDelete(BaseSchema):
    """批量删除请求"""

    ids: list[int] = Field(description="ID列表")


# ==================== 用户导入 ====================


class UserImportResult(BaseSchema):
    """用户导入结果"""

    valid_count: int = Field(default=0, description="成功导入数量")
    invalid_count: int = Field(default=0, description="失败数量")
    message_list: list[str] = Field(default=[], description="错误信息列表")


# ==================== 操作日志 ====================


class OperationLogPageQuery(BaseSchema):
    """操作日志分页查询"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    username: str | None = Field(default=None, description="用户名")
    operation: str | None = Field(default=None, description="操作描述")
    method: str | None = Field(default=None, description="请求方法")
    status: int | None = Field(default=None, description="状态")
    start_time: datetime | None = Field(default=None, description="开始时间")
    end_time: datetime | None = Field(default=None, description="结束时间")


class OperationLogOut(TimestampSchema):
    """操作日志响应数据"""

    user_id: int | None = Field(default=None, description="用户ID")
    username: str = Field(default="", description="用户名")
    name: str = Field(default="", description="用户姓名")
    operation: str = Field(default="", description="操作描述")
    method: str = Field(default="", description="请求方法")
    path: str = Field(default="", description="请求路径")
    query_params: str = Field(default="", description="查询参数")
    request_body: str = Field(default="", description="请求体")
    response_status: int = Field(default=0, description="响应状态码")
    response_body: str = Field(default="", description="响应体")
    ip: str = Field(default="", description="IP地址")
    browser: str = Field(default="", description="浏览器")
    os: str = Field(default="", description="操作系统")
    execution_time: int = Field(default=0, description="执行时间(毫秒)")
    status: int = Field(default=1, description="状态(1:成功;0:失败)")
    error_msg: str = Field(default="", description="错误信息")


class OperationLogPageResult(BaseSchema):
    """操作日志分页结果"""

    list: List[OperationLogOut] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数")

    @property
    def results(self) -> List[OperationLogOut]:
        return self.list

    @property
    def count(self) -> int:
        return self.total


class VisitTrendOut(BaseSchema):
    """访问趋势统计"""

    date: str = Field(description="日期")
    count: int = Field(default=0, description="访问次数")


class VisitStatsOut(BaseSchema):
    """访问统计"""

    total_count: int = Field(default=0, description="总访问次数")
    today_count: int = Field(default=0, description="今日访问次数")
    week_count: int = Field(default=0, description="本周访问次数")
    month_count: int = Field(default=0, description="本月访问次数")
    success_count: int = Field(default=0, description="成功次数")
    fail_count: int = Field(default=0, description="失败次数")
    avg_execution_time: float = Field(default=0, description="平均执行时间(毫秒)")
    top_users: list[dict[str, Any]] = Field(default=[], description="活跃用户TOP10")
    top_paths: list[dict[str, Any]] = Field(default=[], description="热门路径TOP10")
