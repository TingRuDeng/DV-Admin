# -*- coding: utf-8 -*-
from drf_yasg.inspectors import SwaggerAutoSchema


class OperationIDAutoSchema(SwaggerAutoSchema):
    """覆盖get_operation_id方法, 添加multiple_delete动作"""

    def get_operation_id(self, operation_keys=None):
        operation_id = super().get_operation_id(operation_keys)
        # 安全检查view是否有action属性
        if hasattr(self.view, 'action'):
            if self.view.action == 'multiple_delete':
                return operation_id.replace('delete', 'multiple_delete')
        return operation_id
