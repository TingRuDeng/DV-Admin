"""用户服务导入导出测试。"""

import uuid
from io import BytesIO

import pytest

from app.core.exceptions import ValidationError
from app.services.system.user_service import user_service

pytest_plugins = ["user_service_fixtures"]

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
    async def test_import_users_valid(self, db, test_dept_for_service, test_role_for_service):
        """测试导入有效用户"""
        from io import BytesIO

        import openpyxl

        # 创建测试 Excel 文件
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["用户名*", "姓名", "邮箱", "手机号", "性别", "部门ID", "角色ID(多个用逗号分隔)"])
        ws.append([
            f"import_{uuid.uuid4().hex[:8]}",
            "导入用户",
            f"import_{uuid.uuid4().hex[:8]}@example.com",
            f"159{uuid.uuid4().hex[:8]}",
            "1",
            str(test_dept_for_service.id),
            str(test_role_for_service.id)
        ])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

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
