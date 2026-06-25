"""
系统管理模型兼容导出入口
"""

from app.db.models.system_dept import Departments
from app.db.models.system_dict import DictData, DictItems
from app.db.models.system_log import OperationLog
from app.db.models.system_notice import NoticeReads, Notices
from app.db.models.system_permission import Permissions, Roles

__all__ = [
    "Departments",
    "DictData",
    "DictItems",
    "NoticeReads",
    "Notices",
    "OperationLog",
    "Permissions",
    "Roles",
]
