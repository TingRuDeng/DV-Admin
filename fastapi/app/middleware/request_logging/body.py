"""
请求日志 body 处理

封装请求体读取、文本截断和响应体复制逻辑。
"""

from typing import Any

from fastapi import Request
from fastapi.responses import Response as FastAPIResponse
from starlette.responses import Response

from app.utils.audit import get_body_capture_skip_info

TRUNCATED_SUFFIX = "...[TRUNCATED]"
BINARY_DATA_MARKER = "[BINARY DATA]"
EXCLUDED_BODY_MARKER = "[EXCLUDED]"
BODY_CAPTURE_SKIPPED_MARKER = "[BODY CAPTURE SKIPPED]"


async def get_request_body(
    request: Request,
    should_exclude: bool,
    log_request_body: bool,
    max_body_length: int,
) -> str:
    """读取请求体并按日志配置返回可记录文本。"""
    if get_body_capture_skip_info(request) is not None:
        if not log_request_body or should_exclude:
            return EXCLUDED_BODY_MARKER
        return BODY_CAPTURE_SKIPPED_MARKER
    try:
        body = await request.body()
    except Exception as error:
        if not log_request_body or should_exclude:
            # 即使普通请求日志排除了 body，也要尽早尝试缓存请求体，
            # 让后续结构化审计上下文可以在端点消费流后继续读取。
            return EXCLUDED_BODY_MARKER
        return f"[ERROR: {str(error)}]"

    if not log_request_body or should_exclude:
        return EXCLUDED_BODY_MARKER
    if not body:
        return ""
    return decode_body(body, max_body_length)


def decode_body(body: bytes, max_body_length: int) -> str:
    """将 body 解码为日志文本，二进制和超长内容显式标记。"""
    try:
        body_str = body.decode("utf-8")
    except UnicodeDecodeError:
        return BINARY_DATA_MARKER

    if len(body_str) > max_body_length:
        return body_str[:max_body_length] + TRUNCATED_SUFFIX
    return body_str


async def clone_response_with_body(response: Any) -> tuple[Response, bytes]:
    """读取响应 body 后重建响应，避免日志消费掉 body iterator。"""
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    cloned_response = FastAPIResponse(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )
    return cloned_response, response_body
