# -*- coding: utf-8 -*-
"""
用户导入功能测试

测试用户导入的各个场景
"""
import io
import uuid
import pytest
import pytest_asyncio
from openpyxl import Workbook


@pytest_asyncio.fixture(scope="function")
async def test_import_setup(db):
    """创建导入测试所需的基础数据"""
    from app.db.models.system import Departments, Roles
    
    # 创建测试部门
    dept = await Departments.create(
        name="测试部门",
        sort=1,
        status=1,
        leader="管理员",
        phone="13800138000",
    )
    
    # 创建测试角色
    role1 = await Roles.create(
        name=f"测试角色1_{uuid.uuid4().hex[:6]}",
        code=f"test_role1_{uuid.uuid4().hex[:6]}",
        status=1,
        sort=1,
    )
    
    role2 = await Roles.create(
        name=f"测试角色2_{uuid.uuid4().hex[:6]}",
        code=f"test_role2_{uuid.uuid4().hex[:6]}",
        status=1,
        sort=2,
    )
    
    return {
        "dept": dept,
        "role1": role1,
        "role2": role2,
    }


async def test_user_import(test_import_setup):
    """
    测试用户导入功能
    """
    from app.services.system.user_service import user_service
    
    dept = test_import_setup["dept"]
    role1 = test_import_setup["role1"]
    role2 = test_import_setup["role2"]

    # 创建测试 Excel 文件
    wb = Workbook()
    ws = wb.active
    ws.title = "用户导入"

    # 设置表头
    headers = ["用户名*", "姓名", "邮箱", "手机号", "性别", "部门ID", "角色ID(多个用逗号分隔)"]
    ws.append(headers)

    # 添加测试数据
    test_data = [
        ["user001", "测试用户1", "user001@example.com", "13800138001", "1", str(dept.id), str(role1.id)],
        ["user002", "测试用户2", "user002@example.com", "13800138002", "2", str(dept.id), f"{role1.id},{role2.id}"],
        ["user003", "测试用户3", "user003@example.com", "13800138003", "0", "", ""],
        # 重复用户名测试
        ["user001", "重复用户", "duplicate@example.com", "13800138004", "1", "", ""],
        # 空用户名测试
        ["", "空用户名", "empty@example.com", "13800138005", "1", "", ""],
        # 无效部门ID测试（会使用默认部门）
        ["user004", "无效部门", "user004@example.com", "13800138006", "1", "99999", str(role1.id)],
    ]

    for data in test_data:
        ws.append(data)

    # 保存到字节流
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    # 执行导入
    result = await user_service.import_users(buffer, dept_id=dept.id)

    # 验证结果
    print(f"成功导入: {result.valid_count} 条")
    print(f"失败数量: {result.invalid_count} 条")
    print(f"错误信息: {result.message_list}")

    assert result.valid_count == 4, f"应该成功导入 4 条数据，实际: {result.valid_count}"
    assert result.invalid_count == 2, f"应该失败 2 条数据，实际: {result.invalid_count}"
    assert len(result.message_list) == 3, f"应该有 3 条错误信息，实际: {len(result.message_list)}"


async def test_import_template():
    """
    测试导入模板生成
    """
    from app.services.system.user_service import user_service

    # 获取模板
    template = await user_service.get_import_template()

    print(f"模板文件名: {template['filename']}")
    print(f"模板内容长度: {len(template['content'])}")

    assert template["filename"] == "用户导入模板.xlsx"
    assert template["content"] is not None


if __name__ == "__main__":
    import asyncio
    import pytest_asyncio

    # 运行测试
    print("测试导入模板生成...")
    asyncio.run(test_import_template())

    print("\n所有测试通过！")
