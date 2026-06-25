"""
系统管理 Schema 兼容导出入口
"""

from app.schemas.system_common import BulkDelete, UserImportResult
from app.schemas.system_dept import DeptCreate, DeptOut, DeptTree, DeptUpdate
from app.schemas.system_dict import (
    DictDataCreate,
    DictDataOut,
    DictDataUpdate,
    DictItemCreate,
    DictItemOut,
    DictItemUpdate,
    DictWithItems,
)
from app.schemas.system_log import (
    OperationLogOut,
    OperationLogPageQuery,
    OperationLogPageResult,
    VisitStatsOut,
    VisitTrendOut,
)
from app.schemas.system_menu import MenuCreate, MenuOut, MenuTree, MenuUpdate
from app.schemas.system_notice import (
    NoticeAdminPageResult,
    NoticeCreate,
    NoticeDetailOut,
    NoticeFormOut,
    NoticeMyPageOut,
    NoticeMyPageResult,
    NoticePageOut,
    NoticeUpdate,
)
from app.schemas.system_role import RoleCreate, RoleOut, RoleUpdate, RoleWithPermissions
from app.schemas.system_user import (
    UserCreate,
    UserFormOut,
    UserOut,
    UserPageQuery,
    UserPartialUpdate,
    UserUpdate,
)

__all__ = [
    "BulkDelete",
    "DeptCreate",
    "DeptOut",
    "DeptTree",
    "DeptUpdate",
    "DictDataCreate",
    "DictDataOut",
    "DictDataUpdate",
    "DictItemCreate",
    "DictItemOut",
    "DictItemUpdate",
    "DictWithItems",
    "MenuCreate",
    "MenuOut",
    "MenuTree",
    "MenuUpdate",
    "NoticeAdminPageResult",
    "NoticeCreate",
    "NoticeDetailOut",
    "NoticeFormOut",
    "NoticeMyPageOut",
    "NoticeMyPageResult",
    "NoticePageOut",
    "NoticeUpdate",
    "OperationLogOut",
    "OperationLogPageQuery",
    "OperationLogPageResult",
    "RoleCreate",
    "RoleOut",
    "RoleUpdate",
    "RoleWithPermissions",
    "UserCreate",
    "UserFormOut",
    "UserImportResult",
    "UserOut",
    "UserPageQuery",
    "UserPartialUpdate",
    "UserUpdate",
    "VisitStatsOut",
    "VisitTrendOut",
]
