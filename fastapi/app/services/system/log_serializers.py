"""
日志服务输出转换 helper
"""

from app.db.models.system import OperationLog
from app.schemas.system import OperationLogOut


def operation_log_to_out(log: OperationLog) -> OperationLogOut:
    """将 OperationLog ORM 对象转换为 API 输出模型。"""
    return OperationLogOut(
        id=log.id,
        user_id=log.user_id,
        username=log.username,
        name=log.name,
        operation=log.operation,
        method=log.method,
        path=log.path,
        query_params=log.query_params,
        request_body=log.request_body,
        response_status=log.response_status,
        response_body=log.response_body,
        ip=log.ip,
        browser=log.browser,
        os=log.os,
        execution_time=log.execution_time,
        status=log.status,
        error_msg=log.error_msg,
        created_at=log.created_at,
        updated_at=log.updated_at,
    )
