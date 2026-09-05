"""审计日志对象关联与结构化请求上下文契约测试。"""

from __future__ import annotations

import hashlib
import json
import uuid

import pytest
from starlette.datastructures import QueryParams
from starlette.requests import Request
from starlette.responses import Response

from app.db.models.system import OperationLog
from app.middleware.request_logging.middleware import RequestLoggingMiddleware
from app.utils.audit import (
    MAX_REQUEST_CONTEXT_BYTES,
    build_request_context,
    limit_request_context,
    serialize_query_params,
    set_audit_context,
    set_audit_object,
)

AUDIT_BODY_CAPTURE_LIMIT = 256 * 1024


def test_query_params_serializer_masks_sensitive_values_and_keeps_duplicates():
    query_params = QueryParams(
        "token=fastapi-secret&search=one&search=two&empty="
    )

    serialized = json.loads(serialize_query_params(query_params))

    assert serialized["token"] == "******"
    assert serialized["search"] == ["one", "two"]
    assert serialized["empty"] == ""
    assert "fastapi-secret" not in json.dumps(serialized)


def make_request(
    path: str = "/api/v1/system/users/7/",
    query_string: bytes = b"tag=one&tag=two",
    method: str = "POST",
    body: bytes = b"",
    headers: list[tuple[bytes, bytes]] | None = None,
) -> Request:
    """构造可供上下文 helper 使用的最小 ASGI 请求。"""

    request_headers = list(headers or [])
    if body and not any(name.lower() == b"content-length" for name, _value in request_headers):
        request_headers.append((b"content-length", str(len(body)).encode()))

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "query_string": query_string,
        "headers": request_headers,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "scheme": "http",
        "path_params": {"user_id": "7"},
    }
    return Request(scope, receive)


@pytest.mark.asyncio
async def test_context_recursively_masks_body_and_sensitive_headers():
    request = make_request(
        body=json.dumps(
            {
                "profile": {
                    "name": "Alice",
                    "password": "must-not-leak",
                    "tokens": [{"accessToken": "also-secret"}],
                }
            }
        ).encode(),
        headers=[
            (b"content-type", b"application/json"),
            (b"accept", b"application/json"),
            (b"authorization", b"Bearer must-not-leak"),
            (b"cookie", b"session=must-not-leak"),
            (b"x-request-id", b"request-context-1"),
        ],
    )

    context = await build_request_context(request)

    assert context["pathParams"] == {"userId": "7"}
    assert context["query"]["tag"] == ["one", "two"]
    assert context["body"]["profile"]["name"] == "Alice"
    assert context["body"]["profile"]["password"] != "must-not-leak"
    assert context["body"]["profile"]["tokens"] == "******"
    assert "authorization" not in context["selectedHeaders"]
    assert "cookie" not in context["selectedHeaders"]
    assert context["selectedHeaders"]["accept"] == "application/json"
    assert len(context["bodyHash"]) == 64


@pytest.mark.asyncio
async def test_context_masks_sensitive_values_inside_selected_headers():
    """白名单 Header 的值也不能把 Referer/XFF 中的凭据原样落库。"""
    request = make_request(
        body=b"{}",
        headers=[
            (b"content-type", b"application/json"),
            (
                b"referer",
                b"https://host.example/path?token=referer-secret&next=/home"
                b"&code=oauth-secret#state=state-secret",
            ),
            (b"x-forwarded-for", b"10.0.0.1, token=forwarded-secret"),
        ],
    )

    context = await build_request_context(request)

    assert context["selectedHeaders"]["referer"] == (
        "https://host.example/path?token=******&next=******&code=******#state=******"
    )
    assert context["selectedHeaders"]["x-forwarded-for"] == "10.0.0.1, ******"
    serialized = json.dumps(context)
    assert "referer-secret" not in serialized
    assert "oauth-secret" not in serialized
    assert "state-secret" not in serialized
    assert "forwarded-secret" not in serialized


@pytest.mark.asyncio
async def test_context_limits_serialized_size_and_marks_truncated():
    request = make_request(
        query_string=b"",
        body=json.dumps({"notes": "x" * (MAX_REQUEST_CONTEXT_BYTES * 2)}).encode(),
        headers=[(b"content-type", b"application/json")],
    )

    context = await build_request_context(request)

    encoded = json.dumps(context, ensure_ascii=False, separators=(",", ":")).encode()
    assert len(encoded) <= MAX_REQUEST_CONTEXT_BYTES
    assert context["truncated"] is True


@pytest.mark.asyncio
async def test_canonical_request_fields_cannot_be_overridden_by_extra_context():
    """请求采集字段和显式对象字段必须优先于业务附加上下文。"""
    body = json.dumps({"name": "actual"}).encode()
    request = make_request(
        query_string=b"tag=actual",
        body=body,
        headers=[(b"content-type", b"application/json")],
    )
    set_audit_object(request, "system.users", 7, changed_fields=["name"])
    set_audit_context(
        request,
        object_type="spoofed.type",
        object_id="999",
        path_params={"userId": "999"},
        query={"tag": "spoofed"},
        body={"name": "spoofed"},
        body_hash="spoofed-hash",
        changed_fields=["spoofedField"],
        custom_marker="kept",
    )

    context = await build_request_context(request)

    assert context["objectType"] == "system.users"
    assert context["objectId"] == "7"
    assert context["pathParams"] == {"userId": "7"}
    assert context["query"] == {"tag": "actual"}
    assert context["body"] == {"name": "actual"}
    assert context["changedFields"] == ["name"]
    assert context["bodyHash"] == hashlib.sha256(body).hexdigest()
    assert context["customMarker"] == "kept"


def test_extreme_context_truncation_preserves_audit_identity_and_batch_summary():
    """顶层附加字段很多时仍保留对象身份和批量结果摘要。"""
    context = {f"extra{i}": "x" * 1000 for i in range(1000)}
    context.update(
        {
            "objectType": "system.users",
            "objectId": "7",
            "bodyHash": "a" * 64,
            "batchCount": 10,
            "processedCount": 10,
            "successCount": 7,
            "failedCount": 3,
            "failureCodes": ["DELETE_FAILED", "PROTECTED_OBJECT"],
        }
    )

    limited = limit_request_context(context)

    assert (
        len(json.dumps(limited, ensure_ascii=False, separators=(",", ":")).encode())
        <= MAX_REQUEST_CONTEXT_BYTES
    )
    assert limited["truncated"] is True
    assert limited["objectType"] == "system.users"
    assert limited["objectId"] == "7"
    assert limited["bodyHash"] == "a" * 64
    assert limited["batchCount"] == 10
    assert limited["processedCount"] == 10
    assert limited["successCount"] == 7
    assert limited["failedCount"] == 3
    assert limited["failureCodes"] == ["DELETE_FAILED", "PROTECTED_OBJECT"]


@pytest.mark.asyncio
async def test_multipart_context_contains_file_metadata_without_file_content():
    boundary = b"----dv-admin-boundary"
    body = (
        b"--" + boundary + b"\r\n"
        b'Content-Disposition: form-data; name="file"; filename="credentials.txt"\r\n'
        b"Content-Type: text/plain\r\n\r\n"
        b"private-file-content\r\n"
        b"--" + boundary + b"--\r\n"
    )
    request = make_request(
        path="/api/v1/system/users/import",
        query_string=b"",
        body=body,
        headers=[
            (b"content-type", b"multipart/form-data; boundary=" + boundary),
            (b"content-length", str(len(body)).encode()),
        ],
    )

    context = await build_request_context(request)

    assert len(context["fileMeta"]) == 1
    metadata = context["fileMeta"][0]
    assert metadata["fieldName"] == "file"
    assert metadata["fileName"] == "credentials.txt"
    assert metadata["size"] == len(b"private-file-content")
    assert len(metadata["sha256"]) == 64
    assert "private-file-content" not in json.dumps(context)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("content_length_header", "reason"),
    [
        (None, "content-length-missing"),
        (b"not-a-number", "content-length-invalid"),
    ],
)
async def test_unbounded_multipart_context_is_skipped_without_reading_body(
    content_length_header: bytes | None,
    reason: str,
):
    """没有可信长度时，审计层不应抢读 multipart 流。"""
    boundary = b"----dv-admin-unbounded-boundary"
    body = b"--" + boundary + b"--\r\n"
    receive_calls = 0

    async def receive():
        nonlocal receive_calls
        receive_calls += 1
        raise AssertionError("审计上下文不应读取无界 multipart body")

    headers = [(b"content-type", b"multipart/form-data; boundary=" + boundary)]
    if content_length_header is not None:
        headers.append((b"content-length", content_length_header))
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/system/users/import",
            "raw_path": b"/api/v1/system/users/import",
            "query_string": b"",
            "headers": headers,
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        },
        receive,
    )

    context = await build_request_context(request)

    assert receive_calls == 0
    assert context["bodyHash"] == ""
    assert context["fileMeta"] == []
    assert context["bodyCapture"] == {
        "status": "skipped",
        "reason": reason,
        "maxBytes": AUDIT_BODY_CAPTURE_LIMIT,
    }
    assert context["truncated"] is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("content_length_header", "reason"),
    [
        (None, "content-length-missing"),
        (b"not-a-number", "content-length-invalid"),
        (b"-1", "content-length-invalid"),
    ],
)
async def test_unbounded_non_multipart_context_is_skipped_without_reading_body(
    content_length_header: bytes | None,
    reason: str,
):
    """非 multipart 请求没有可信长度时，审计层也不能无界读取 body。"""
    receive_calls = 0

    async def receive():
        nonlocal receive_calls
        receive_calls += 1
        raise AssertionError("审计上下文不应读取无界非 multipart body")

    headers = [(b"content-type", b"application/json")]
    if content_length_header is not None:
        headers.append((b"content-length", content_length_header))
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/system/users/",
            "raw_path": b"/api/v1/system/users/",
            "query_string": b"",
            "headers": headers,
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        },
        receive,
    )

    context = await build_request_context(request)

    assert receive_calls == 0
    assert context["bodyHash"] == ""
    assert context["body"] == {}
    assert context["bodyCapture"] == {
        "status": "skipped",
        "reason": reason,
        "maxBytes": AUDIT_BODY_CAPTURE_LIMIT,
    }
    assert context["truncated"] is True


def test_set_audit_object_keeps_explicit_context_on_request():
    request = make_request()

    set_audit_object(request, "system.users", 7, changed_fields=["name", "mobile"])

    assert request.state.audit_object == {"type": "system.users", "id": "7"}
    assert request.state.audit_context["changedFields"] == ["name", "mobile"]


def test_changed_fields_use_public_camel_case_names():
    request = make_request()

    set_audit_object(request, "system.users", 7, changed_fields=["role_ids", "parent_id"])

    assert request.state.audit_context["changedFields"] == ["roleIds", "parentId"]


def test_write_request_persists_object_context(auth_client):
    suffix = uuid.uuid4().hex[:8]
    response = auth_client.post(
        "/api/v1/system/dicts/",
        json={"name": f"对象关联字典{suffix}", "dictCode": f"audit_object_{suffix}", "status": 1},
        headers={"X-Request-ID": f"object-context-{suffix}"},
    )
    assert response.status_code in (200, 201)

    page = auth_client.get(
        "/api/v1/system/logs/page",
        params={"requestId": f"object-context-{suffix}"},
    )
    assert page.status_code == 200
    rows = page.json()["data"]["list"]
    assert len(rows) == 1
    row = rows[0]
    assert row["objectType"] == "system.dicts"
    assert row["objectId"]
    assert row["requestContext"]["objectId"] == row["objectId"]


def test_request_logging_middleware_exposes_structured_context_method():
    middleware = RequestLoggingMiddleware(lambda _scope, _receive, _send: None)
    assert hasattr(middleware, "_build_request_context")


@pytest.mark.asyncio
async def test_oversize_multipart_context_does_not_read_full_request_body():
    """超限 multipart 只记录可观察的跳过状态，不在审计层缓存整包 body。"""
    boundary = b"----dv-admin-large-boundary"
    content_length = AUDIT_BODY_CAPTURE_LIMIT + 1
    receive_calls = 0

    async def receive():
        nonlocal receive_calls
        receive_calls += 1
        raise AssertionError("审计上下文不应读取超限 multipart body")

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/information/change-avatar/",
            "raw_path": b"/api/v1/information/change-avatar/",
            "query_string": b"",
            "headers": [
                (b"content-type", b"multipart/form-data; boundary=" + boundary),
                (b"content-length", str(content_length).encode()),
            ],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        },
        receive,
    )

    context = await build_request_context(request)

    assert receive_calls == 0
    assert context["bodyHash"] == ""
    assert context["bodyCapture"] == {
        "status": "skipped",
        "reason": "content-length-exceeds-limit",
        "contentLength": content_length,
        "maxBytes": AUDIT_BODY_CAPTURE_LIMIT,
    }
    assert context["truncated"] is True


@pytest.mark.asyncio
async def test_oversize_multipart_middleware_leaves_body_for_endpoint(monkeypatch):
    """跳过审计采集时，业务端点仍能完整消费原始上传流。"""
    boundary = b"----dv-admin-large-middleware-boundary"
    body = b"x" * (AUDIT_BODY_CAPTURE_LIMIT + 1)
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/upload",
            "raw_path": b"/api/v1/upload",
            "query_string": b"",
            "headers": [
                (b"content-type", b"multipart/form-data; boundary=" + boundary),
                (b"content-length", str(len(body)).encode()),
            ],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        },
        lambda: _request_message(body),
    )
    middleware = RequestLoggingMiddleware(lambda _scope, _receive, _send: None)
    captured: dict[str, object] = {}

    async def persist(_request, _response, _context, _start_time, request_context=None):
        captured["request_context"] = request_context

    async def call_next(incoming_request: Request) -> Response:
        captured["body"] = await incoming_request.body()
        return Response("ok")

    monkeypatch.setattr(middleware, "_persist_operation_log", persist)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert captured["body"] == body
    assert captured["request_context"] == {
        "pathParams": {},
        "query": {},
        "body": {},
        "selectedHeaders": {
            "content-type": f"multipart/form-data; boundary={boundary.decode()}"
        },
        "fileMeta": [],
        "changedFields": [],
        "bodyHash": "",
        "bodyCapture": {
            "status": "skipped",
            "reason": "content-length-exceeds-limit",
            "contentLength": len(body),
            "maxBytes": AUDIT_BODY_CAPTURE_LIMIT,
        },
        "truncated": True,
    }


async def _request_message(body: bytes) -> dict[str, object]:
    return {"type": "http.request", "body": body, "more_body": False}
