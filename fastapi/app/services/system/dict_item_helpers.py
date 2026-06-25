"""
字典项服务共享辅助函数
"""

from app.schemas.system import DictItemUpdate


def extract_item_update_fields(item_data: DictItemUpdate) -> dict[str, object]:
    """提取非空更新字段，保持原服务忽略 None 的行为。"""
    return {
        field: value
        for field, value in item_data.model_dump(exclude_unset=True).items()
        if value is not None
    }
