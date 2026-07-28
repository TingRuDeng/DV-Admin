"""用户服务导入导出测试。"""

import base64
import csv
import uuid
from io import BytesIO, StringIO

import pytest
from openpyxl import Workbook

from app.core.exceptions import ValidationError
from app.db.models.oauth import Users
from app.services.system.user_service import user_service

pytest_plugins = ["user_service_fixtures"]


def build_import_file(rows: list[list[str]]) -> BytesIO:
    """按标准模板构造用户导入文件。"""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(
        ["用户名*", "姓名", "邮箱", "手机号", "性别", "部门ID", "角色ID(多个用逗号分隔)"]
    )
    for row in rows:
        worksheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


def decode_export_rows(result: dict) -> list[list[str]]:
    """解码导出 CSV。"""
    content = base64.b64decode(result["content"]).decode("utf-8")
    return list(csv.reader(StringIO(content)))


class TestUserServiceImportExport:
    """测试用户导入导出"""

    @pytest.mark.asyncio
    async def test_get_import_template(self, db):
        """测试获取导入模板"""
        result = await user_service.get_import_template()

        assert "filename" in result
        assert "content" in result
        assert result["filename"].endswith(".xlsx")

    @pytest.mark.asyncio
    async def test_export_users(self, db, test_user_for_service):
        """测试导出用户"""
        result = await user_service.export_users()

        assert "filename" in result
        assert "content" in result
        assert result["filename"].endswith(".csv")

    @pytest.mark.asyncio
    async def test_export_users_filters_scope_and_masks_contacts(
        self,
        db,
        scoped_user_context,
    ):
        """导出不得包含范围外用户，且复用敏感字段读取权限。"""
        visible_user = scoped_user_context["visible_user"]
        visible_user.email = "visible@example.com"
        visible_user.mobile = "13800138000"
        await visible_user.save()

        result = await user_service.export_users(
            current_user=scoped_user_context["operator"],
        )

        rows = decode_export_rows(result)
        exported = {row[0]: row for row in rows[1:]}
        assert visible_user.username in exported
        assert scoped_user_context["hidden_user"].username not in exported
        assert exported[visible_user.username][2] == "v******@example.com"
        assert exported[visible_user.username][3] == "138****8000"

    @pytest.mark.asyncio
    async def test_import_users_valid(self, db, test_dept_for_service, test_role_for_service):
        """测试导入有效用户"""
        buffer = build_import_file(
            [
                [
                    f"import_{uuid.uuid4().hex[:8]}",
                    "导入用户",
                    f"import_{uuid.uuid4().hex[:8]}@example.com",
                    f"159{uuid.uuid4().hex[:8]}",
                    "1",
                    str(test_dept_for_service.id),
                    str(test_role_for_service.id),
                ]
            ]
        )

        result = await user_service.import_users(buffer, dept_id=test_dept_for_service.id)

        assert result.valid_count >= 1
        assert result.invalid_count == 0

    @pytest.mark.asyncio
    async def test_import_users_invalid_file(self, db):
        """测试导入无效文件"""
        # 创建无效的文件内容
        buffer = BytesIO(b"invalid content")

        with pytest.raises(ValidationError):
            await user_service.import_users(buffer)

    @pytest.mark.asyncio
    async def test_import_rejects_rows_outside_department_scope(
        self,
        db,
        scoped_user_context,
    ):
        """导入行指定范围外部门时整行失败。"""
        username = f"hidden_import_{uuid.uuid4().hex[:8]}"
        buffer = build_import_file(
            [
                [
                    username,
                    "范围外导入",
                    "",
                    "",
                    "0",
                    str(scoped_user_context["hidden_dept"].id),
                    "",
                ]
            ]
        )

        result = await user_service.import_users(
            buffer,
            current_user=scoped_user_context["operator"],
        )

        assert result.valid_count == 0
        assert result.invalid_count == 1
        assert any("目标部门超出" in message for message in result.message_list)
        assert not await Users.filter(username=username).exists()

    @pytest.mark.asyncio
    async def test_import_rejects_sensitive_fields_without_write_permission(
        self,
        db,
        scoped_user_context,
    ):
        """导入不能绕过手机号和邮箱字段写入权限。"""
        username = f"sensitive_import_{uuid.uuid4().hex[:8]}"
        buffer = build_import_file(
            [
                [
                    username,
                    "敏感导入",
                    "sensitive@example.com",
                    "13800138001",
                    "0",
                    str(scoped_user_context["visible_dept"].id),
                    "",
                ]
            ]
        )

        result = await user_service.import_users(
            buffer,
            current_user=scoped_user_context["operator"],
        )

        assert result.valid_count == 0
        assert result.invalid_count == 1
        assert any("字段写入权限" in message for message in result.message_list)
        assert not await Users.filter(username=username).exists()

    @pytest.mark.asyncio
    async def test_import_rejects_row_with_nonexistent_role(
        self,
        db,
        test_dept_for_service,
    ):
        """导入角色 ID 必须全部有效，不能静默过滤后继续创建。"""
        username = f"invalid_role_import_{uuid.uuid4().hex[:8]}"
        buffer = build_import_file(
            [
                [
                    username,
                    "无效角色导入",
                    "",
                    "",
                    "0",
                    str(test_dept_for_service.id),
                    "999999",
                ]
            ]
        )

        result = await user_service.import_users(buffer)

        assert result.valid_count == 0
        assert result.invalid_count == 1
        assert any("角色ID" in message for message in result.message_list)
        assert not await Users.filter(username=username).exists()

    @pytest.mark.asyncio
    async def test_import_rejects_row_with_malformed_role(
        self,
        db,
        test_dept_for_service,
    ):
        """角色 ID 格式错误时也必须拒绝整行。"""
        username = f"malformed_role_import_{uuid.uuid4().hex[:8]}"
        buffer = build_import_file(
            [
                [
                    username,
                    "格式错误角色导入",
                    "",
                    "",
                    "0",
                    str(test_dept_for_service.id),
                    "1,invalid",
                ]
            ]
        )

        result = await user_service.import_users(buffer)

        assert result.valid_count == 0
        assert result.invalid_count == 1
        assert any("角色ID格式错误" in message for message in result.message_list)
        assert not await Users.filter(username=username).exists()
