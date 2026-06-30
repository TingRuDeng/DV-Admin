
from django.urls import include, path

from drf_admin.apps.system.views import departments, dicts, logs, menus, notices, roles, users
from drf_admin.utils import routers

router = routers.AdminRouter()
router.register(r'users', users.UsersViewSet, basename="users")  # 用户管理
router.register(r'roles', roles.RolesViewSet, basename="roles")  # 角色管理
router.register(r'menus', menus.MenusViewSet, basename="menus")  # 菜单管理
router.register(r'dicts', dicts.DictsViewSet, basename="dicts")  # 字典管理
router.register(r'dict-items', dicts.DictItemsViewSet, basename="dict-items")  # 字典项管理
router.register(r'departments', departments.DepartmentsViewSet, basename="departments")  # 部门管理

urlpatterns = [
    path('users/options/', users.UsersOptionsViewSet.as_view()),  # 用户下拉框列表
    path('roles/options/', roles.RolesOptionsViewSet.as_view()),  # 角色下拉框列表
    path('menus/options/', menus.MenusOptionsViewSet.as_view()),  # 菜单下拉框列表

    path('users/<int:pk>/password/reset/', users.ResetPasswordAPIView.as_view()),  # 重置密码
    path('users/<int:pk>/permissions/', users.PermissionsAPIView.as_view()),  # 用户权限ID列表
    path('notices/my-page/', notices.NoticesAPIView.as_view()),  # 通知列表
    path('notices/page', notices.NoticesViewSet.as_view({'get': 'list'})),  # 通知公告分页
    path('notices', notices.NoticesViewSet.as_view({'post': 'create'})),  # 创建通知公告
    path('notices/<int:pk>/publish', notices.NoticesViewSet.as_view({'put': 'publish'})),  # 发布通知公告
    path('notices/<int:pk>/revoke', notices.NoticesViewSet.as_view({'put': 'revoke'})),  # 撤回通知公告
    path('notices/<str:ids>', notices.NoticesViewSet.as_view({
        'put': 'update_by_id',
        'delete': 'delete_by_ids',
    })),  # 更新或删除通知公告
    # path('dept/options/', departments.DepartmentsTreeViewSet.as_view()),  # 部门树状列表
    path('roles/<int:pk>/menu-ids/', roles.RoleMenuIdsAPIView.as_view()),  # 角色菜单ID列表

    # 操作日志（与 FastAPI 对齐；显式路径需先于 logs/<ids> 注册）
    path('logs/page', logs.LogPageAPIView.as_view()),  # 操作日志分页
    path('logs/visit-trend', logs.VisitTrendAPIView.as_view()),  # 访问趋势
    path('logs/visit-stats', logs.VisitStatsAPIView.as_view()),  # 访问统计
    path('logs/clear/<int:days>', logs.LogClearAPIView.as_view()),  # 清理历史日志
    path('logs/<str:ids>', logs.LogDeleteAPIView.as_view()),  # 批量删除日志

    path('', include(router.urls)),
]
