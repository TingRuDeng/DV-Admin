# -*- coding: utf-8 -*-
"""
认证授权 Schema 模块

定义认证相关的 Pydantic 模型。
"""

from datetime import datetime
from typing import List, Optional

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampSchema


class Token(BaseSchema):
    """
    令牌响应模型

    登录成功后的令牌信息。
    """

    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="访问令牌过期时间（秒）")
    refresh_expires_in: int = Field(description="刷新令牌过期时间（秒）")


class TokenPayload(BaseSchema):
    """
    令牌载荷模型

    JWT 令牌的载荷数据。
    """

    sub: Optional[str] = Field(default=None, description="用户ID")
    exp: Optional[datetime] = Field(default=None, description="过期时间")
    type: Optional[str] = Field(default=None, description="令牌类型")
    iat: Optional[datetime] = Field(default=None, description="签发时间")


class UserLogin(BaseSchema):
    """
    用户登录请求模型

    用户登录时的请求数据。
    """

    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    captcha_key: Optional[str] = Field(default=None, description="验证码key")
    captcha_code: Optional[str] = Field(default=None, description="验证码")


class UserInfo(TimestampSchema):
    """
    用户信息模型

    用户的基本信息。
    """

    username: str = Field(description="用户名")
    name: Optional[str] = Field(default=None, description="真实姓名")
    email: Optional[str] = Field(default="", description="邮箱")
    mobile: Optional[str] = Field(default="", description="手机号")
    avatar: str = Field(default="avatar/default.png", description="头像")
    gender: int = Field(default=0, description="性别")
    is_active: int = Field(default=1, description="是否激活")
    dept_id: Optional[int] = Field(default=None, description="部门ID")
    dept_name: Optional[str] = Field(default="", description="部门名称")
    role_names: Optional[str] = Field(default=None, description="角色名称")
    roles: str = Field(default="[]", description="角色列表(JSON字符串)")
    perms: List[str] = Field(default=[], description="权限列表")

    @field_validator("role_names", mode="before")
    @classmethod
    def validate_role_names(cls, v):
        """验证角色名称"""
        if isinstance(v, list):
            return "、".join(v)
        return v


class UserProfile(UserInfo):
    """
    用户个人资料模型

    包含更详细的用户信息。
    """

    permissions: List[str] = Field(default=[], description="权限列表")
    roles: List[dict] = Field(default=[], description="角色列表")


class ChangePassword(BaseSchema):
    """
    修改密码请求模型
    """

    old_password: str = Field(description="旧密码")
    new_password: str = Field(min_length=6, max_length=20, description="新密码")
    confirm_password: str = Field(min_length=6, max_length=20, description="确认新密码")

    @field_validator("confirm_password")
    @classmethod
    def validate_password_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("两次输入的密码不一致")
        return v


class UpdateProfile(BaseSchema):
    """
    更新个人信息请求模型
    """

    name: Optional[str] = Field(default=None, description="真实姓名")
    email: Optional[str] = Field(default=None, description="邮箱")
    mobile: Optional[str] = Field(default=None, description="手机号")
    gender: Optional[int] = Field(default=None, description="性别")
    avatar: Optional[str] = Field(default=None, description="头像URL")

