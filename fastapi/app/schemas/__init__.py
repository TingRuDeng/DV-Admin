"""
Pydantic 模型模块

定义 API 请求和响应的数据验证模型。
"""

from app.schemas.base import (
    BaseSchema,
    PageQuery,
    PageResult,
    ResponseModel,
)
from app.schemas.oauth import (
    Token,
    TokenPayload,
    UserInfo,
    UserLogin,
)
from app.schemas.system import (
    DeptCreate,
    DeptOut,
    DeptUpdate,
    DictDataCreate,
    DictDataOut,
    DictItemCreate,
    DictItemOut,
    MenuCreate,
    MenuOut,
    MenuUpdate,
    RoleCreate,
    RoleOut,
    RoleUpdate,
    UserCreate,
    UserOut,
    UserUpdate,
)

__all__ = [
    # 基础
    "BaseSchema",
    "PageQuery",
    "PageResult",
    "ResponseModel",
    # 认证
    "Token",
    "TokenPayload",
    "UserLogin",
    "UserInfo",
    # 系统管理
    "UserCreate",
    "UserUpdate",
    "UserOut",
    "RoleCreate",
    "RoleUpdate",
    "RoleOut",
    "MenuCreate",
    "MenuUpdate",
    "MenuOut",
    "DeptCreate",
    "DeptUpdate",
    "DeptOut",
    "DictDataCreate",
    "DictDataOut",
    "DictItemCreate",
    "DictItemOut",
]
