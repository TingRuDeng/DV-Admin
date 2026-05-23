"""
请求日志敏感路径测试
"""

from fastapi import Response

from app.middleware.logging_middleware import RequestLoggingMiddleware


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
