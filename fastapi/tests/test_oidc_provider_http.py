"""OIDC 身份提供方 HTTP 辅助函数：超时、不跟随重定向、错误映射和日志不泄露响应内容。"""

from urllib.parse import parse_qs

import httpx
import pytest
from loguru import logger

from app.core.config import settings
from app.core.oidc_policy import HTTP_TIMEOUT_SECONDS, OidcError
from app.services import oidc_provider

IDP_SECRET = "idp-response-secret-value"


@pytest.fixture
def idp_transport(monkeypatch):
    """用 MockTransport 替换网络层，同时保留生产代码传给 AsyncClient 的参数。"""
    state: dict = {"requests": [], "client_kwargs": [], "handler": None}
    real_client = httpx.AsyncClient

    class RecordingClient(real_client):
        def __init__(self, **kwargs):
            state["client_kwargs"].append(kwargs)
            super().__init__(transport=httpx.MockTransport(handle), **kwargs)

    def handle(request: httpx.Request) -> httpx.Response:
        state["requests"].append(request)
        return state["handler"](request)

    monkeypatch.setattr(oidc_provider.httpx, "AsyncClient", RecordingClient)
    return state


@pytest.fixture
def captured_logs():
    messages: list[str] = []
    sink_id = logger.add(lambda message: messages.append(str(message)), level="DEBUG")
    try:
        yield messages
    finally:
        logger.remove(sink_id)


async def test_get_json_sends_accept_header_with_timeout_and_no_redirects(idp_transport):
    idp_transport["handler"] = lambda request: httpx.Response(200, json={"issuer": "x"})

    assert await oidc_provider._get_json("https://idp.example.test/doc") == {"issuer": "x"}

    request = idp_transport["requests"][0]
    assert request.method == "GET"
    assert request.headers["Accept"] == "application/json"
    assert idp_transport["client_kwargs"] == [
        {"timeout": HTTP_TIMEOUT_SECONDS, "follow_redirects": False}
    ]


async def test_post_form_is_form_encoded_and_keeps_client_auth_header(idp_transport):
    idp_transport["handler"] = lambda request: httpx.Response(200, json={"id_token": "t"})

    payload = await oidc_provider._post_form(
        "https://idp.example.test/token",
        {"grant_type": "authorization_code", "code": "abc"},
        {"Accept": "application/json", "Authorization": "Basic Y2xpZW50OnNlY3JldA=="},
    )

    assert payload == {"id_token": "t"}
    request = idp_transport["requests"][0]
    assert request.method == "POST"
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert request.headers["Authorization"] == "Basic Y2xpZW50OnNlY3JldA=="
    assert parse_qs(request.content.decode()) == {
        "grant_type": ["authorization_code"],
        "code": ["abc"],
    }


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(302, headers={"Location": "https://evil.example.test/"}),
        httpx.Response(400, json={"error": "invalid_grant", "error_description": IDP_SECRET}),
        httpx.Response(500, text=IDP_SECRET),
        httpx.Response(200, text=f"<html>{IDP_SECRET}</html>"),
    ],
    ids=["redirect", "client-error", "server-error", "not-json"],
)
@pytest.mark.parametrize("call", ["get", "post"])
async def test_unusable_responses_fail_without_logging_body(
    idp_transport, captured_logs, response, call
):
    idp_transport["handler"] = lambda request: response

    with pytest.raises(OidcError) as error:
        if call == "get":
            await oidc_provider._get_json("https://idp.example.test/doc")
        else:
            await oidc_provider._post_form("https://idp.example.test/token", {"code": "c"}, {})

    assert error.value.message == "身份提供方校验失败"
    assert len(idp_transport["requests"]) == 1
    assert captured_logs
    assert not [message for message in captured_logs if IDP_SECRET in message]


@pytest.mark.parametrize("call", ["get", "post"])
async def test_network_errors_fail_closed(idp_transport, captured_logs, call):
    def refuse(request):
        raise httpx.ConnectError(IDP_SECRET, request=request)

    idp_transport["handler"] = refuse

    with pytest.raises(OidcError):
        if call == "get":
            await oidc_provider._get_json("https://idp.example.test/doc")
        else:
            await oidc_provider._post_form("https://idp.example.test/token", {"code": "c"}, {})

    assert any("ConnectError" in message for message in captured_logs)
    assert not [message for message in captured_logs if IDP_SECRET in message]


@pytest.mark.parametrize("call", ["get", "post"])
async def test_malformed_endpoint_url_fails_closed(call):
    with pytest.raises(OidcError):
        if call == "get":
            await oidc_provider._get_json("https://idp.example.test:bad-port/certs")
        else:
            await oidc_provider._post_form("https://idp.example.test:bad-port/token", {}, {})


def test_config_problem_is_logged_once(monkeypatch, captured_logs):
    monkeypatch.setattr(settings, "oidc_enabled", True)
    monkeypatch.setattr(settings, "oidc_issuer", "")
    oidc_provider.reset_metadata_cache()
    try:
        for _ in range(3):
            with pytest.raises(OidcError):
                oidc_provider.ensure_provider_configured()
    finally:
        oidc_provider.reset_metadata_cache()

    assert len([message for message in captured_logs if "OIDC_ISSUER 未配置" in message]) == 1
