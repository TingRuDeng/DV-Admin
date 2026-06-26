"""
请求日志敏感路径测试
"""

import pytest
from fastapi import Response
from starlette.requests import Request
from starlette.responses import StreamingResponse

from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware as SplitRequestLoggingMiddleware
from app.middleware.request_logging.body import (
    BINARY_DATA_MARKER,
    TRUNCATED_SUFFIX,
    clone_response_with_body,
    decode_body,
)
from app.middleware.request_logging.client import get_client_ip, parse_user_agent


def make_request(
    path: str = "/api/v1/demo",
    headers: list[tuple[bytes, bytes]] | None = None,
) -> Request:
    """构造最小 HTTP 请求对象。"""
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": headers or [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        }
    )


def test_oauth_login_request_body_is_excluded_from_logs():
    middleware = RequestLoggingMiddleware(lambda _scope, _receive, _send: None)
    assert middleware._should_exclude_body("/api/v1/oauth/login/") is True


def test_oauth_refresh_request_body_is_excluded_from_logs():
    middleware = RequestLoggingMiddleware(lambda _scope, _receive, _send: None)
    assert middleware._should_exclude_body("/api/v1/oauth/refresh-token/") is True


def test_profile_password_request_body_is_excluded_from_logs():
    middleware = RequestLoggingMiddleware(lambda _scope, _receive, _send: None)
    assert middleware._should_exclude_body("/api/v1/information/password") is True


def test_custom_excluded_paths_do_not_leak_between_middleware_instances():
    first = RequestLoggingMiddleware(
        lambda _scope, _receive, _send: None,
        exclude_body_paths=["/api/v1/private"],
    )
    second = RequestLoggingMiddleware(lambda _scope, _receive, _send: None)

    assert first._should_exclude_body("/api/v1/private/token") is True
    assert second._should_exclude_body("/api/v1/private/token") is False


def test_custom_excluded_logging_paths_do_not_leak_between_instances():
    first = RequestLoggingMiddleware(
        lambda _scope, _receive, _send: None,
        exclude_paths=["/api/v1/internal"],
    )
    second = RequestLoggingMiddleware(lambda _scope, _receive, _send: None)

    assert first._should_skip_logging("/api/v1/internal/ping") is True
    assert second._should_skip_logging("/api/v1/internal/ping") is False


def test_get_client_ip_prefers_forwarded_for_header():
    request = make_request(
        headers=[
            (b"x-forwarded-for", b"10.0.0.1, 10.0.0.2"),
            (b"x-real-ip", b"10.0.0.3"),
        ]
    )

    assert get_client_ip(request) == "10.0.0.1"


def test_get_client_ip_uses_real_ip_when_forwarded_for_missing():
    request = make_request(headers=[(b"x-real-ip", b"10.0.0.3")])

    assert get_client_ip(request) == "10.0.0.3"


def test_parse_user_agent_extracts_browser_os_and_device():
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    assert parse_user_agent(user_agent) == {
        "browser": "Chrome",
        "os": "MacOS",
        "device": "Desktop",
    }


def test_decode_body_marks_binary_and_truncates_text():
    assert decode_body(b"\xff", max_body_length=10) == BINARY_DATA_MARKER
    assert decode_body(b"abcdef", max_body_length=3) == f"abc{TRUNCATED_SUFFIX}"


@pytest.mark.asyncio
async def test_clone_response_with_body_keeps_response_content():
    response = StreamingResponse(iter([b"hello"]), media_type="text/plain")

    cloned_response, response_body = await clone_response_with_body(response)

    assert response_body == b"hello"
    assert cloned_response.status_code == 200
    assert cloned_response.body == b"hello"


def test_compat_import_points_to_split_implementation():
    assert RequestLoggingMiddleware is SplitRequestLoggingMiddleware
