"""
菜单管理 Service
"""
from typing import Any

from app.core.exceptions import BusinessError, NotFound, ValidationError
from app.db.models.system import Permissions
from app.schemas.system import MenuCreate, MenuOut, MenuTree, MenuUpdate


class MenuService:
    """菜单管理服务"""

    async def get_tree(self) -> list[MenuTree]:
        """
        获取菜单树形列表
        """
        menus = await Permissions.all()
        return self._build_menu_tree(menus)

    async def get(self, menu_id: int) -> MenuOut:
        """
        获取菜单详情
        """
        menu = await Permissions.get_or_none(id=menu_id)
        if not menu:
            raise NotFound("菜单不存在")

        return MenuOut(
            id=menu.id,
            name=menu.name,
            type=menu.type,
            route_name=menu.route_name,
            route_path=menu.route_path,
            component=menu.component,
            sort=menu.sort,
            visible=menu.visible,
            icon=menu.icon,
            redirect=menu.redirect,
            perm=menu.perm,
            keep_alive=menu.keep_alive,
            always_show=menu.always_show,
            params=menu.params,
            desc=menu.desc,
            parent_id=menu.parent_id,
            created_at=menu.created_at,
            updated_at=menu.updated_at,
        )

    async def create(self, menu_data: MenuCreate) -> MenuOut:
        """
        创建菜单
        """
        # 检查父菜单是否存在
        if menu_data.parent_id:
            parent = await Permissions.get_or_none(id=menu_data.parent_id)
            if not parent:
                raise ValidationError("父菜单不存在")

        menu = await Permissions.create(
            name=menu_data.name,
            type=menu_data.type,
            route_name=menu_data.route_name,
            route_path=menu_data.route_path,
            component=menu_data.component,
            sort=menu_data.sort,
            visible=menu_data.visible,
            icon=menu_data.icon,
            redirect=menu_data.redirect,
            perm=menu_data.perm,
            keep_alive=menu_data.keep_alive,
            always_show=menu_data.always_show,
            params=menu_data.params,
            desc=menu_data.desc,
            parent_id=menu_data.parent_id,
        )

        return MenuOut(
            id=menu.id,
            name=menu.name,
            type=menu.type,
            route_name=menu.route_name,
            route_path=menu.route_path,
            component=menu.component,
            sort=menu.sort,
            visible=menu.visible,
            icon=menu.icon,
            redirect=menu.redirect,
            perm=menu.perm,
            keep_alive=menu.keep_alive,
            always_show=menu.always_show,
            params=menu.params,
            desc=menu.desc,
            parent_id=menu.parent_id,
            created_at=menu.created_at,
            updated_at=menu.updated_at,
        )

    async def update(self, menu_id: int, menu_data: MenuUpdate) -> MenuOut:
        """
        更新菜单
        """
        menu = await Permissions.get_or_none(id=menu_id)
        if not menu:
            raise NotFound("菜单不存在")

        # 检查不能将自己设为父菜单
        if menu_data.parent_id == menu_id:
            raise ValidationError("不能将自己设为父菜单")

        update_fields = {}
        for field, value in menu_data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields[field] = value

        if update_fields:
            await Permissions.filter(id=menu_id).update(**update_fields)
            await menu.refresh_from_db()

        return MenuOut(
            id=menu.id,
            name=menu.name,
            type=menu.type,
            route_name=menu.route_name,
            route_path=menu.route_path,
            component=menu.component,
            sort=menu.sort,
            visible=menu.visible,
            icon=menu.icon,
            redirect=menu.redirect,
            perm=menu.perm,
            keep_alive=menu.keep_alive,
            always_show=menu.always_show,
            params=menu.params,
            desc=menu.desc,
            parent_id=menu.parent_id,
            created_at=menu.created_at,
            updated_at=menu.updated_at,
        )

    async def delete(self, menu_id: int) -> None:
        """
        删除菜单
        """
        menu = await Permissions.get_or_none(id=menu_id)
        if not menu:
            raise NotFound("菜单不存在")

        # 检查是否有子菜单
        children = await Permissions.filter(parent_id=menu_id).count()
        if children > 0:
            raise BusinessError("该菜单下存在子菜单，无法删除")

        await menu.delete()

    async def get_permissions(self) -> list[str]:
        """
        获取所有权限标识
        """
        perms = await Permissions.filter(perm__isnull=False).values_list("perm", flat=True)
        return [p for p in perms if p]

    async def get_options(self) -> list[dict[str, Any]]:
        """
        获取菜单下拉选项
        """
        menus = await Permissions.all()
        return self._build_options(menus)

    def _build_menu_tree(self, menus: list[Permissions], parent_id: int | None = None) -> list[MenuTree]:
        """构建菜单树"""
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                children = self._build_menu_tree(menus, menu.id)
                menu_data = {
                    "id": menu.id,
                    "name": menu.name,
                    "type": menu.type,
                    "route_name": menu.route_name,
                    "route_path": menu.route_path,
                    "component": menu.component,
                    "sort": menu.sort,
                    "visible": menu.visible,
                    "icon": menu.icon,
                    "redirect": menu.redirect,
                    "perm": menu.perm,
                    "keep_alive": menu.keep_alive,
                    "always_show": menu.always_show,
                    "params": menu.params,
                    "desc": menu.desc,
                    "parent_id": menu.parent_id,
                    "created_at": menu.created_at,
                    "updated_at": menu.updated_at,
                    "children": children if children else [],
                }
                tree.append(menu_data)
        return sorted(tree, key=lambda x: x["sort"])

    def _build_options(self, menus: list[Permissions], parent_id: int | None = None, level: int = 0) -> list[dict[str, Any]]:
        """构建菜单选项"""
        options = []
        for menu in menus:
            if menu.parent_id == parent_id:
                prefix = "  " * level
                options.append({
                    "value": menu.id,
                    "label": f"{prefix}{menu.name}",
                })
                options.extend(self._build_options(menus, menu.id, level + 1))
        return options


# 导出服务实例
menu_service = MenuService()
