"""
认证授权 Schema 模块

定义认证相关的 Pydantic 模型。
"""

from datetime import datetime
from typing import Any

from pydantic import Field, JsonValue, field_validator

from app.core.oidc_policy import MESSAGE_FLOW_INVALID, OidcError
from app.schemas.base import BaseSchema, TimestampSchema
from app.schemas.password import NewPassword, Password


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

    sub: str | None = Field(default=None, description="用户ID")
    exp: datetime | None = Field(default=None, description="过期时间")
    type: str | None = Field(default=None, description="令牌类型")
    iat: datetime | None = Field(default=None, description="签发时间")


class UserLogin(BaseSchema):
    """
    用户登录请求模型

    用户登录时的请求数据。
    """

    username: str = Field(description="用户名")
    password: Password = Field(description="密码")
    captcha_key: str | None = Field(default=None, description="验证码key")
    captcha_code: str | None = Field(default=None, description="验证码")


class RefreshTokenRequest(BaseSchema):
    """
    刷新令牌请求模型
    """

    refresh_token: str = Field(description="刷新令牌")


class LogoutRequest(BaseSchema):
    """
    退出登录请求模型：带上当前会话的刷新令牌，退出后它不能再换新令牌
    """

    refresh_token: str | None = Field(default=None, description="当前会话的刷新令牌")


class UserInfo(TimestampSchema):
    """
    用户信息模型

    用户的基本信息。
    """

    username: str = Field(description="用户名")
    name: str | None = Field(default=None, description="真实姓名")
    email: str | None = Field(default="", description="邮箱")
    mobile: str | None = Field(default="", description="手机号")
    avatar: str = Field(default="avatar/default.png", description="头像")
    gender: int = Field(default=0, description="性别")
    is_active: int = Field(default=1, description="是否激活")
    dept_id: int | None = Field(default=None, description="部门ID")
    dept_name: str | None = Field(default="", description="部门名称")
    role_names: str | None = Field(default=None, description="角色名称")
    roles: str | list[dict[str, Any]] = Field(default="[]", description="角色列表")
    perms: list[str] = Field(default=[], description="权限列表")

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

    permissions: list[str] = Field(default=[], description="权限列表")


class ChangePassword(BaseSchema):
    """
    修改密码请求模型
    """

    old_password: Password = Field(description="旧密码")
    new_password: NewPassword = Field(description="新密码")
    confirm_password: Password = Field(description="确认新密码")

    @field_validator("confirm_password")
    @classmethod
    def validate_password_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("两次输入的密码不一致")
        return v


class PasswordPolicy(BaseSchema):
    min_length: int = Field(description="新密码最少 Unicode 字符数")
    max_length: int = Field(description="新密码最多 Unicode 字符数")


class UpdateProfile(BaseSchema):
    """
    更新个人信息请求模型
    """

    name: str | None = Field(default=None, description="真实姓名")
    email: str | None = Field(default=None, description="邮箱")
    mobile: str | None = Field(default=None, description="手机号")
    gender: int | None = Field(default=None, description="性别")


class AvatarInfo(BaseSchema):
    """头像上传的双后端共享响应字段。"""

    avatar: str = Field(description="头像存储标识")
    url: str = Field(description="可直接展示的头像URL")


OIDC_FIELD_MAX_LENGTH = 2048
_OIDC_TEXT_SCHEMA: dict[str, JsonValue] = {"type": "string", "maxLength": OIDC_FIELD_MAX_LENGTH}


class OidcAuthorization(BaseSchema):
    """单点登录发起结果；flowSecret 只下发给发起方，回调时原样带回。"""

    authorization_url: str = Field(description="跳转到身份提供方的授权地址")
    state: str = Field(description="本次登录流程的 state")
    flow_secret: str = Field(description="与 state 绑定的一次性流程密钥")


class OidcLogin(BaseSchema):
    """
    单点登录回调请求模型

    字段一律可缺省且不做框架类型校验，由端点统一校验并返回 40000，
    避免框架校验返回与其它单点登录失败不同的错误结构。
    """

    authorization_code: Any = Field(
        default="", description="身份提供方回调的授权码", json_schema_extra=_OIDC_TEXT_SCHEMA
    )
    state: Any = Field(default="", description="回调携带的 state", json_schema_extra=_OIDC_TEXT_SCHEMA)
    flow_secret: Any = Field(
        default="", description="发起时下发的 flowSecret", json_schema_extra=_OIDC_TEXT_SCHEMA
    )
    iss: Any = Field(
        default=None, description="回调携带的 iss（RFC 9207，可选）", json_schema_extra=_OIDC_TEXT_SCHEMA
    )

    def flow_fields(self) -> tuple[str, str, str, str | None]:
        """返回 (授权码, state, flowSecret, iss)；必填项须为非空且不超长的字符串。"""
        required = (self.authorization_code, self.state, self.flow_secret)
        if not all(_bounded_text(value) and value for value in required):
            raise OidcError(MESSAGE_FLOW_INVALID)
        if self.iss is not None and not _bounded_text(self.iss):
            raise OidcError(MESSAGE_FLOW_INVALID)
        return self.authorization_code, self.state, self.flow_secret, self.iss


def _bounded_text(value: object) -> bool:
    return isinstance(value, str) and len(value) <= OIDC_FIELD_MAX_LENGTH
