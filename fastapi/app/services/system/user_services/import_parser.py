"""用户导入 Excel 解析 helper。"""

from dataclasses import dataclass
from typing import Any, BinaryIO

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.core.security import get_password_hash
from app.db.models.oauth import Users
from app.db.models.system import Departments, Roles


@dataclass(frozen=True)
class ImportColumns:
    """记录用户导入模板列索引，避免业务逻辑直接操作魔法字符串。"""

    username: int
    name: int | None
    email: int | None
    mobile: int | None
    gender: int | None
    dept: int | None
    role: int | None


@dataclass
class ImportContext:
    """承载导入过程需要复用的数据库快照。"""

    all_depts: dict[int, Departments]
    all_roles: dict[int, Roles]
    existing_usernames: set[str]
    existing_mobiles: set[str]


@dataclass
class ImportRowResult:
    """单行导入解析结果。"""

    user: Users
    role_ids: list[int]


class UserImportParserMixin:
    """提供用户导入 Excel 解析和保存 helper。"""

    def _load_import_worksheet(self, file: BinaryIO) -> Any:
        """读取 Excel 工作表，并把解析失败转成业务异常。"""
        from openpyxl import load_workbook

        try:
            wb = load_workbook(file)
        except Exception as exc:
            raise ValidationError(f"Excel 文件解析失败: {str(exc)}") from exc
        return wb.active

    def _parse_import_columns(self, worksheet: Any) -> ImportColumns:
        """解析导入模板表头并校验必填列。"""
        headers = [cell.value for cell in worksheet[1]]
        if not headers or headers[0] is None:
            raise ValidationError("Excel 文件格式错误，缺少表头")

        if "用户名*" not in headers:
            raise ValidationError("Excel 文件缺少必要字段: 用户名*")

        return ImportColumns(
            username=headers.index("用户名*"),
            name=headers.index("姓名") if "姓名" in headers else None,
            email=headers.index("邮箱") if "邮箱" in headers else None,
            mobile=headers.index("手机号") if "手机号" in headers else None,
            gender=headers.index("性别") if "性别" in headers else None,
            dept=headers.index("部门ID") if "部门ID" in headers else None,
            role=headers.index("角色ID(多个用逗号分隔)") if "角色ID(多个用逗号分隔)" in headers else None,
        )

    async def _build_import_context(self) -> ImportContext:
        """预加载导入校验需要的部门、角色和唯一字段集合。"""
        username_values = await Users.all().values_list("username", flat=True)
        mobile_values = await Users.filter(mobile__isnull=False).values_list("mobile", flat=True)
        return ImportContext(
            all_depts={dept.id: dept for dept in await Departments.all()},
            all_roles={role.id: role for role in await Roles.filter(status=1).all()},
            existing_usernames={str(username) for username in username_values},
            existing_mobiles={str(mobile) for mobile in mobile_values if mobile},
        )

    def _parse_import_row(
        self,
        row_idx: int,
        row: tuple[Any, ...],
        columns: ImportColumns,
        dept_id: int | None,
        context: ImportContext,
        messages: list[str],
    ) -> ImportRowResult | None:
        """解析单行导入数据，失败时只记录该行错误并继续处理后续行。"""
        try:
            return self._parse_import_row_inner(row_idx, row, columns, dept_id, context, messages)
        except Exception as exc:
            messages.append(f"第{row_idx}行: 数据处理错误 - {str(exc)}")
            return None

    def _parse_import_row_inner(
        self,
        row_idx: int,
        row: tuple[Any, ...],
        columns: ImportColumns,
        dept_id: int | None,
        context: ImportContext,
        messages: list[str],
    ) -> ImportRowResult | None:
        username = self._read_required_username(row_idx, row, columns, context, messages)
        if not username:
            return None

        mobile = self._read_optional_text(row, columns.mobile)
        if mobile and mobile in context.existing_mobiles:
            messages.append(f"第{row_idx}行: 手机号 '{mobile}' 已存在")
            return None

        role_ids = self._parse_role_ids(row_idx, row, columns.role, context.all_roles, messages)
        user = Users(
            username=username,
            password=get_password_hash(settings.default_password),
            name=self._read_optional_text(row, columns.name) or username,
            email=self._read_optional_text(row, columns.email),
            mobile=mobile,
            gender=self._parse_gender(row, columns.gender),
            is_active=1,
            dept_id=self._parse_dept_id(row_idx, row, columns.dept, dept_id, context.all_depts, messages),
            avatar="avatar/default.png",
        )
        self._remember_imported_user(username, mobile, context)
        return ImportRowResult(user=user, role_ids=role_ids)

    def _read_required_username(
        self,
        row_idx: int,
        row: tuple[Any, ...],
        columns: ImportColumns,
        context: ImportContext,
        messages: list[str],
    ) -> str | None:
        """读取并校验用户名唯一性。"""
        username = self._read_optional_text(row, columns.username)
        if not username:
            messages.append(f"第{row_idx}行: 用户名不能为空")
            return None
        if username in context.existing_usernames:
            messages.append(f"第{row_idx}行: 用户名 '{username}' 已存在")
            return None
        return username

    def _parse_gender(self, row: tuple[Any, ...], gender_idx: int | None) -> int:
        """解析性别字段，非法值按历史行为归为未知。"""
        if gender_idx is None or row[gender_idx] is None:
            return 0
        try:
            gender = int(row[gender_idx])
        except (ValueError, TypeError):
            return 0
        return gender if gender in [0, 1, 2] else 0

    def _parse_dept_id(
        self,
        row_idx: int,
        row: tuple[Any, ...],
        dept_idx: int | None,
        default_dept_id: int | None,
        all_depts: dict[int, Departments],
        messages: list[str],
    ) -> int | None:
        """解析部门 ID，不存在或格式错误时沿用默认部门。"""
        if dept_idx is None or row[dept_idx] is None:
            return default_dept_id
        try:
            import_dept_id = int(row[dept_idx])
        except (ValueError, TypeError):
            messages.append(f"第{row_idx}行: 部门ID格式错误，使用默认部门")
            return default_dept_id
        if import_dept_id not in all_depts:
            messages.append(f"第{row_idx}行: 部门ID '{import_dept_id}' 不存在，使用默认部门")
            return default_dept_id
        return import_dept_id

    def _parse_role_ids(
        self,
        row_idx: int,
        row: tuple[Any, ...],
        role_idx: int | None,
        all_roles: dict[int, Roles],
        messages: list[str],
    ) -> list[int]:
        """解析角色 ID，并过滤不存在或已禁用角色。"""
        if role_idx is None or row[role_idx] is None:
            return []
        try:
            role_ids = [int(rid.strip()) for rid in str(row[role_idx]).strip().split(",") if rid.strip()]
        except (ValueError, TypeError):
            messages.append(f"第{row_idx}行: 角色ID格式错误")
            return []

        invalid_roles = [role_id for role_id in role_ids if role_id not in all_roles]
        if invalid_roles:
            messages.append(f"第{row_idx}行: 角色ID {invalid_roles} 不存在或已禁用")
        return [role_id for role_id in role_ids if role_id in all_roles]

    async def _save_import_users(
        self,
        rows: list[ImportRowResult],
        all_roles: dict[int, Roles],
    ) -> None:
        """保存导入用户并写入角色关联。"""
        for row in rows:
            await row.user.save()
            if row.role_ids:
                roles = [all_roles[role_id] for role_id in row.role_ids if role_id in all_roles]
                await row.user.roles.add(*roles)

    def _remember_imported_user(
        self,
        username: str,
        mobile: str | None,
        context: ImportContext,
    ) -> None:
        """记录本次导入已占用的唯一字段，避免同文件内重复导入。"""
        context.existing_usernames.add(username)
        if mobile:
            context.existing_mobiles.add(mobile)

    def _read_optional_text(self, row: tuple[Any, ...], column_idx: int | None) -> str | None:
        """读取可选文本字段并去除首尾空白。"""
        if column_idx is None or not row[column_idx]:
            return None
        return str(row[column_idx]).strip()

