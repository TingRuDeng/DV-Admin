"""用户导入导出服务。"""

from typing import Any, BinaryIO

from app.db.models.oauth import Users
from app.schemas.system import UserImportResult
from app.services.system.data_scope import (
    apply_user_data_scope,
    get_visible_department_ids,
)
from app.services.system.field_permission import (
    USER_FIELD_PLAIN_PERMISSION,
    can_view_plain_fields,
    can_write_sensitive_user_fields,
    mask_email,
    mask_mobile,
)
from app.services.system.user_services.import_parser import ImportRowResult, UserImportParserMixin


class UserImportExportMixin(UserImportParserMixin):
    """承载用户 Excel 导入、模板下载和 CSV 导出。"""

    async def import_users(
        self,
        file: BinaryIO,
        dept_id: int | None = None,
        current_user: Users | None = None,
    ) -> UserImportResult:
        """导入 Excel 用户数据，并返回成功和失败明细。"""
        worksheet = self._load_import_worksheet(file)
        try:
            columns = self._parse_import_columns(worksheet)
            context = await self._build_import_context()
            visible_dept_ids = await get_visible_department_ids(current_user)
            can_write_sensitive = await can_write_sensitive_user_fields(current_user)
            users_to_create: list[ImportRowResult] = []
            messages: list[str] = []
            invalid_count = 0

            for row_idx, row in enumerate(
                worksheet.iter_rows(min_row=2, values_only=True),
                start=2,
            ):
                row_result = self._parse_import_row(
                    row_idx,
                    row,
                    columns,
                    dept_id,
                    context,
                    messages,
                    visible_dept_ids=visible_dept_ids,
                    can_write_sensitive=can_write_sensitive,
                )
                if row_result:
                    users_to_create.append(row_result)
                else:
                    invalid_count += 1

            await self._save_import_users(users_to_create, context.all_roles)
            return UserImportResult(
                valid_count=len(users_to_create),
                invalid_count=invalid_count,
                message_list=messages,
            )
        finally:
            worksheet.parent.close()

    async def get_import_template(self) -> dict[str, Any]:
        """获取用户导入模板。"""
        import base64
        import io

        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "用户导入模板"
        ws.append(["用户名*", "姓名", "邮箱", "手机号", "性别", "部门ID", "角色ID(多个用逗号分隔)"])
        ws.append(["zhangsan", "张三", "zhangsan@example.com", "13800138000", "1", "1", "1,2"])

        for column, width in self._template_column_widths().items():
            ws.column_dimensions[column].width = width

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        b64_content = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "filename": "用户导入模板.xlsx",
            "content": b64_content,
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

    async def export_users(
        self,
        current_user: Users | None = None,
    ) -> dict[str, Any]:
        """导出用户 CSV。"""
        import base64
        import csv
        import io

        query = await apply_user_data_scope(Users.all(), current_user)
        users = await query.order_by("id")
        can_view_plain = await can_view_plain_fields(
            current_user,
            USER_FIELD_PLAIN_PERMISSION,
        )
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["用户名", "姓名", "邮箱", "手机号", "状态", "创建时间"])

        for user in users:
            writer.writerow(self._build_export_row(user, can_view_plain))

        b64_content = base64.b64encode(("\ufeff" + buffer.getvalue()).encode("utf-8")).decode(
            "utf-8"
        )
        return {
            "filename": "用户导出.csv",
            "content": b64_content,
            "content_type": "text/csv;charset=utf-8",
        }

    def _template_column_widths(self) -> dict[str, int]:
        """返回导入模板列宽配置。"""
        return {
            "A": 15,
            "B": 15,
            "C": 25,
            "D": 15,
            "E": 10,
            "F": 10,
            "G": 25,
        }

    def _build_export_row(
        self,
        user: Users,
        can_view_plain: bool = True,
    ) -> list[str]:
        """把用户模型转换为 CSV 行。"""
        return [
            user.username,
            user.name or "",
            (user.email if can_view_plain else mask_email(user.email)) or "",
            (user.mobile if can_view_plain else mask_mobile(user.mobile)) or "",
            "启用" if user.is_active else "禁用",
            user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
        ]
