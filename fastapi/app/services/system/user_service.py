"""用户管理 Service 聚合入口。"""

from app.services.system.user_services.import_export import UserImportExportMixin
from app.services.system.user_services.mutation import UserMutationMixin
from app.services.system.user_services.query import UserQueryMixin


class UserService(UserQueryMixin, UserMutationMixin, UserImportExportMixin):
    """用户管理服务。

    对外保留历史 `user_service` 单例入口，内部实现按职责拆分到
    `app.services.system.user_services` 子模块。
    """


user_service = UserService()
