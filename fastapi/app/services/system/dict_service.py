"""
字典管理聚合服务
"""

from app.services.system.dict_item_flat_service import DictItemFlatService
from app.services.system.dict_item_service import DictItemService
from app.services.system.dict_type_service import DictTypeService


class DictService(DictTypeService, DictItemService, DictItemFlatService):
    """组合字典类型、字典项和扁平字典项能力的统一服务入口。"""


# 导出服务实例，保持 API 层和测试层现有导入路径不变。
dict_service = DictService()
