import os
import sys
import asyncio

# 添加路径以便导入 app
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(os.path.join(project_root, "fastapi"))

from tortoise import Tortoise, run_async
from app.core.config import settings
from app.db.models.system import Departments, Permissions, Roles
from app.db.models.oauth import Users

async def verify():
    await Tortoise.init(config=settings.tortoise_orm_config)
    
    print("--- Verification Report ---")
    
    user_count = await Users.all().count()
    print(f"Users: {user_count} (Expected: 2)")
    
    role_count = await Roles.all().count()
    print(f"Roles: {role_count} (Expected: 2)")
    
    perm_count = await Permissions.all().count()
    print(f"Permissions: {perm_count} (Expected: 66)")
    
    dept_count = await Departments.all().count()
    print(f"Departments: {dept_count} (Expected: 1)")

    # 验证 M2M
    try:
        admin = await Users.get(username="admin")
        await admin.fetch_related("roles")
        print(f"Admin roles: {[r.name for r in admin.roles]}")
        
        if admin.roles:
            role = admin.roles[0]
            await role.fetch_related("permissions")
            print(f"Role '{role.name}' permissions count: {len(role.permissions)}")
    except Exception as e:
        print(f"Verification failed: {e}")

    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(verify())
