"""
请求日志 body 处理

封装请求体读取、文本截断和响应体复制逻辑。
"""

from typing import Any

from fastapi import Request
from fastapi.responses import Response as FastAPIResponse
from starlette.responses import Response

TRUNCATED_SUFFIX = "...[TRUNCATED]"
BINARY_DATA_MARKER = "[BINARY DATA]"
EXCLUDED_BODY_MARKER = "[EXCLUDED]"


async def get_request_body(
    request: Request,
    should_exclude: bool,
    log_request_body: bool,
    max_body_length: int,
) -> str:
    """读取请求体并按日志配置返回可记录文本。"""
    if not log_request_body or should_exclude:
        return EXCLUDED_BODY_MARKER

    try:
        body = await request.body()
        if not body:
            return ""
        return decode_body(body, max_body_length)
    except Exception as error:
        return f"[ERROR: {str(error)}]"


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
