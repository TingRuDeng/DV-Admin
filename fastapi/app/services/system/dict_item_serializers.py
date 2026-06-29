"""
字典项序列化辅助函数
"""

from app.db.models.system import DictItems
from app.schemas.system import DictItemOut


def serialize_dict_item(item: DictItems, dict_name: str | None = None) -> DictItemOut:
    """将字典项 ORM 对象转换为响应模型。"""
    return DictItemOut(
        id=item.id,
        label=item.label,
        value=item.value,
        status=item.status,
        tag_type=item.tag_type,
        dict_data_id=item.dict_data_id,
        dict_name=dict_name,
        create_time=item.created_at,
        update_time=item.updated_at,
    )
