"""
字典项序列化辅助函数
"""

from app.db.models.system import DictItems
from app.schemas.system import DictItemOut


def serialize_dict_item(item: DictItems) -> DictItemOut:
    """将字典项 ORM 对象转换为响应模型。"""
    return DictItemOut(
        id=item.id,
        label=item.label,
        value=item.value,
        status=item.status,
        dict_data_id=item.dict_data_id,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
