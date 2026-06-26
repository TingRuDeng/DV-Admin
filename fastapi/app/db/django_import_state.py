from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any

from app.db.models.base import BaseModel


@dataclass
class ImportTasks:
    """导入过程中延后处理的关系任务。"""

    m2m: list[tuple[BaseModel, str, list[int]]] = dataclass_field(default_factory=list)
    fk: list[tuple[type[BaseModel], int, str, int]] = dataclass_field(default_factory=list)


@dataclass(frozen=True)
class ModelImportContext:
    """单个 Django 模型导入所需的上下文。"""

    model_name: str
    model_class: type[BaseModel]
    tasks: ImportTasks


@dataclass
class ModelWriteBuffers:
    """单条数据转换后的写入参数。"""

    create: dict[str, Any]
    update: dict[str, Any] = dataclass_field(default_factory=dict)
    m2m: dict[str, list[int]] = dataclass_field(default_factory=dict)


@dataclass(frozen=True)
class FieldAssignContext:
    """字段转换时需要共享的模型和主键信息。"""

    model_name: str
    model_class: type[BaseModel]
    pk: int
    buffers: ModelWriteBuffers
    tasks: ImportTasks
