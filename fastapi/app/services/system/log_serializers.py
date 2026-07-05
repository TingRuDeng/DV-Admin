"""
日志服务输出转换 helper
"""

from app.db.models.system import OperationLog
from app.schemas.system import OperationLogOut
from app.services.system.field_permission import mask_ip, mask_payload


def operation_log_to_out(log: OperationLog, can_view_plain: bool = True) -> OperationLogOut:
    """将 OperationLog ORM 对象转换为 API 输出模型。"""
    request_body = _visible_text(log.request_body, can_view_plain, mask_payload)
    response_body = _visible_text(log.response_body, can_view_plain, mask_payload)
    ip = _visible_text(log.ip, can_view_plain, mask_ip)
    return OperationLogOut(
        id=log.id,
        user_id=log.user_id,
        username=log.username,
        name=log.name,
        operation=log.operation,
        method=log.method,
        path=log.path,
        query_params=log.query_params,
        request_body=request_body,
        response_status=log.response_status,
        response_body=response_body,
        ip=ip,
        browser=log.browser,
        os=log.os,
        execution_time=log.execution_time,
        status=log.status,
        error_msg=log.error_msg,
        created_at=log.created_at,
        updated_at=log.updated_at,
    )


def _visible_text(value: str | None, can_view_plain: bool, masker) -> str:
    """将可空日志字段归一为输出模型要求的字符串。"""
    if can_view_plain:
        return value or ""
    return masker(value) or ""
