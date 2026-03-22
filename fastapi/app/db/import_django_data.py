# -*- coding: utf-8 -*-
import json
import os
import sys
import asyncio
from typing import List, Dict, Any, Type

# 添加路径以便导入 app
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(os.path.join(project_root, "fastapi"))

from tortoise import Tortoise, run_async
from app.core.config import settings
from app.db.models.system import Departments, Permissions, Roles, DictData, DictItems
from app.db.models.oauth import Users
from app.db.models.base import BaseModel

# 映射模型名称到类
MODEL_MAPPING: Dict[str, Type[BaseModel]] = {
    "system.departments": Departments,
    "system.permissions": Permissions,
    "system.roles": Roles,
    "system.users": Users,
    "system.dicts": DictData,
    "system.dictitems": DictItems,
}

# 字段名映射
FIELD_MAPPING = {
    "create_time": "created_at",
    "update_time": "updated_at",
    "dict": "dict_data",  # DictItems 的外键: Django(dict) -> FastAPI(dict_data)
    "dict_code": "code",  # DictData: Django(dict_code) -> FastAPI(code)
}

async def init():
    """初始化数据库连接"""
    await Tortoise.init(config=settings.tortoise_orm_config)
    print("Database connection initialized.")

async def import_data():
    """导入数据"""
    json_path = os.path.join(project_root, "backend", "init_data.json")
    if not os.path.exists(json_path):
        print(f"Error: File not found: {json_path}")
        return

    print(f"Reading data from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 存储 M2M 关系和外键更新任务
    m2m_tasks = []
    fk_updates = []
    
    # 按模型分类数据
    grouped_data = {k: [] for k in MODEL_MAPPING.keys()}
    for item in data:
        model_name = item.get("model")
        if model_name in grouped_data:
            grouped_data[model_name].append(item)

    # 定义导入顺序
    import_order = [
        "system.departments",
        "system.permissions",
        "system.dicts",
        "system.dictitems", # 依赖 dicts
        "system.roles",     # 依赖 permissions (M2M)
        "system.users",     # 依赖 departments, roles (M2M)
    ]

    for model_name in import_order:
        items = grouped_data.get(model_name, [])
        if not items:
            continue
            
        ModelClass = MODEL_MAPPING[model_name]
        print(f"Importing {len(items)} items for {model_name}...")
        
        for item in items:
            pk = item["pk"]
            fields_data = item["fields"]
            
            # 准备创建参数
            create_kwargs = {"id": pk}
            update_kwargs = {} # 用于 update，不包含 id
            m2m_fields = {}
            
            for k, v in fields_data.items():
                # 特殊映射处理
                if model_name == "system.dicts" and k == "remark":
                    new_k = "desc"
                else:
                    new_k = FIELD_MAPPING.get(k, k)
                
                # 检查 M2M 字段 (优先检查，防止误判)
                if new_k in ModelClass._meta.m2m_fields:
                    m2m_fields[new_k] = v
                    continue

                # 检查普通字段
                if new_k in ModelClass._meta.fields_map:
                    # 外键处理
                    if new_k in ModelClass._meta.fk_fields:
                        # 如果是自关联 (parent)，先设为 None，后续更新
                        if model_name in ["system.departments", "system.permissions"] and new_k == "parent" and v is not None:
                            fk_updates.append((ModelClass, pk, new_k, v))
                            v = None
                        
                        # 设置外键 ID
                        key = f"{new_k}_id"
                        val = v if v is not None else None
                        create_kwargs[key] = val
                        update_kwargs[key] = val
                        continue
                    
                    # 特殊值转换
                    if model_name == "system.users" and new_k == "is_active":
                        # Django bool -> FastAPI int
                        v = 1 if v else 0
                    
                    create_kwargs[new_k] = v
                    update_kwargs[new_k] = v
                
                else:
                    # 忽略未知字段
                    # print(f"  Skipping unknown field: {k} -> {new_k}")
                    pass

            # 创建或更新对象
            try:
                # 检查是否存在
                exists = await ModelClass.filter(id=pk).exists()
                if exists:
                    # 更新 (不包含 id)
                    if update_kwargs:
                        await ModelClass.filter(id=pk).update(**update_kwargs)
                    obj = await ModelClass.get(id=pk)
                else:
                    # 创建
                    obj = await ModelClass.create(**create_kwargs)
                
                # 收集 M2M 任务
                for field, ids in m2m_fields.items():
                    if ids:
                        m2m_tasks.append((obj, field, ids))
                        
            except Exception as e:
                print(f"  Error importing {model_name} id={pk}: {e}")

    # 处理自关联外键更新 (parent)
    print(f"Updating {len(fk_updates)} self-referencing foreign keys...")
    for ModelClass, pk, field, fk_id in fk_updates:
        try:
            # 使用 update 直接更新数据库，避免触发其他验证
            await ModelClass.filter(id=pk).update(**{f"{field}_id": fk_id})
        except Exception as e:
            print(f"  Error updating FK for {ModelClass.__name__} id={pk}: {e}")

    # 处理 M2M
    print(f"Processing {len(m2m_tasks)} M2M relationships...")
    for obj, field, ids in m2m_tasks:
        try:
            # 获取关联管理器
            relation = getattr(obj, field)
            # 获取关联模型的类
            RelatedModel = relation.remote_model
            # 查询关联对象
            related_objs = await RelatedModel.filter(id__in=ids)
            # 清除旧关系并添加新关系
            await relation.clear()
            await relation.add(*related_objs)
        except Exception as e:
            print(f"  Error processing M2M for {obj} field={field}: {e}")

    print("Import completed successfully!")

async def main():
    await init()
    await import_data()
    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(main())
