"""用户查询服务。"""

from typing import Any

from tortoise.expressions import Q

from app.core.exceptions import NotFound
from app.db.models.oauth import Users
from app.db.models.system import Departments
from app.schemas.base import PageResult
from app.schemas.system import UserFormOut, UserOut
from app.services.system.user_services.serializers import UserSerializerMixin


class UserQueryMixin(UserSerializerMixin):
    """承载用户分页、详情和下拉选项查询。"""




    async def get_page(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        is_active: int | None = None,
        dept_id: int | None = None,
    ) -> PageResult[UserOut]:
        """
        获取用户分页列表
        """
        # 构建查询条件
        query = Users.all()

        if search:
            query = query.filter(
                Q(username__icontains=search)
                | Q(name__icontains=search)
                | Q(mobile__icontains=search)
                | Q(email__icontains=search)
            )

        if is_active is not None:
            query = query.filter(is_active=is_active)

        if dept_id:
            query = query.filter(dept_id=dept_id)

        # 计算总数
        total = await query.count()

        # 分页查询。部门名已经在下方批量查询，这里避免额外预取 direct relation，
        # 否则在 sqlite 测试环境里会触发跨事件循环锁错误。
        users = await query.prefetch_related("roles").offset((page - 1) * page_size).limit(page_size).all()

        # 预加载所有部门（避免每个用户单独查询）
        dept_ids = [u.dept_id for u in users if u.dept_id]
        depts = {}
        if dept_ids:
            depts = {d.id: d.name for d in await Departments.filter(id__in=dept_ids).all()}

        # 序列化结果
        user_list = []
        for user in users:
            user_data = await self._serialize_user_optimized(user, depts)
            user_list.append(user_data)

        return PageResult.create(
            total=total,
            page=page,
            page_size=page_size,
            results=user_list,
        )

    async def get(self, user_id: int) -> UserOut:
        """
        获取用户详情
        """
        user = await Users.get_or_none(id=user_id)
        if not user:
            raise NotFound("用户不存在")

        return await self._serialize_user(user)


    async def get_form(self, user_id: int) -> UserFormOut:
        """
        获取用户表单详情（用于编辑回填）
        """
        user = await Users.get_or_none(id=user_id)
        if not user:
            raise NotFound("用户不存在")

        return await self._serialize_user_form(user)


    async def get_options(self) -> list[dict[str, Any]]:
        """
        获取用户下拉选项
        """
        users = await Users.filter(is_active=1).all()

        return [
            {
                "value": user.id,
                "label": f"{user.name or user.username}({user.username})",
            }
            for user in users
        ]
