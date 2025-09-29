
from drf_admin.utils import routers
from django.urls import path, include
from drf_admin.apps.system.views import users, roles, departments, menus, notices, dicts

router = routers.AdminRouter()
router.register(r'users', users.UsersViewSet, basename="users")  # 用户管理
router.register(r'roles', roles.RolesViewSet, basename="roles")  # 角色管理
router.register(r'menus', menus.MenusViewSet, basename="menus")  # 菜单管理
router.register(r'dicts', dicts.DictsViewSet, basename="dicts")  # 字典管理
router.register(r'dict-items', dicts.DictItemsViewSet, basename="dict-items")  # 字典项管理
router.register(r'dept', departments.DepartmentsViewSet, basename="departments")  # 部门管理

urlpatterns = [
    path('roles/options/', roles.RolesOptionsViewSet.as_view()),  # 角色下拉框列表

    path('users/reset-password/<int:pk>/', users.ResetPasswordAPIView.as_view()),  # 重置密码
    path('users/<int:pk>/permissions/', users.PermissionsAPIView.as_view()),  # 用户权限ID列表
    path('notices/my-page/', notices.NoticesAPIView.as_view()),  # 通知列表
    path('dept/options/', departments.DepartmentsTreeViewSet.as_view()),  # 部门树状列表
    path('roles/<int:pk>/menuIds/', roles.RoleMenuIdsAPIView.as_view()),  # 角色菜单ID列表

    path('', include(router.urls)),
]