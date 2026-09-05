"""审计日志的业务对象关联与结构化请求上下文。"""

from __future__ import annotations

import copy
import hashlib
import ipaddress
import json
import re
from collections.abc import Mapping
from email.parser import BytesParser
from email.policy import default as email_policy
from typing import Any
from urllib.parse import parse_qs

from fastapi import Request

MAX_REQUEST_CONTEXT_BYTES = 16 * 1024
# 审计层只读取有界的小请求；大文件仍由业务端点按自己的流式限制处理。
MAX_AUDIT_BODY_CAPTURE_BYTES = 256 * 1024
MAX_OBJECT_TYPE_LENGTH = 100
MAX_OBJECT_ID_LENGTH = 255
MAX_CONTEXT_DEPTH = 10
_BODYLESS_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})

# 这些字段由请求采集器或显式对象关联生成，业务附加上下文不能覆盖。
_RESERVED_CONTEXT_KEYS = frozenset(
    {
        "pathParams",
        "query",
        "body",
        "selectedHeaders",
        "fileMeta",
        "changedFields",
        "bodyHash",
        "bodyCapture",
        "objectType",
        "objectId",
        "truncated",
    }
)
_PRIORITY_CONTEXT_KEYS = (
    "objectType",
    "objectId",
    "bodyHash",
    "bodyCapture",
    "pathParams",
    "changedFields",
    "batchCount",
    "batchIds",
    "processedCount",
    "successCount",
    "failedCount",
    "failureCodes",
)

_SENSITIVE_KEYWORDS = (
    "password",
    "passwd",
    "token",
    "secret",
    "authorization",
    "cookie",
    "apikey",
    "accesskey",
    "privatekey",
    "clientsecret",
)
_SELECTED_HEADERS = {
    "content-type": "content-type",
    "accept": "accept",
    "user-agent": "user-agent",
    "x-request-id": "x-request-id",
    "x-forwarded-for": "x-forwarded-for",
    "referer": "referer",
}


def _normalise_key(key: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


def _is_sensitive_key(key: object) -> bool:
    normalized = _normalise_key(key)
    return any(keyword in normalized for keyword in _SENSITIVE_KEYWORDS)


def _to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def get_changed_fields(data: Any) -> list[str]:
    """从请求模型或映射提取对外字段名，统一为 camelCase。"""
    if data is None:
        return []
    if hasattr(data, "model_dump"):
        data = data.model_dump(exclude_unset=True)
    if isinstance(data, Mapping) or hasattr(data, "keys"):
        fields = list(data.keys())
    elif isinstance(data, (list, tuple, set)):
        fields = list(data)
    else:
        return []
    return [_to_camel(str(field))[:100] for field in fields[:100]]


def mask_sensitive_data(data: Any, depth: int = 0) -> Any:
    """递归掩码敏感键，避免把请求原文带入审计上下文。"""
    if depth > MAX_CONTEXT_DEPTH:
        return "***MAX_DEPTH***"
    if isinstance(data, Mapping):
        return {
            str(key): "******" if _is_sensitive_key(key) else mask_sensitive_data(value, depth + 1)
            for key, value in data.items()
        }
    if isinstance(data, (list, tuple)):
        return [mask_sensitive_data(value, depth + 1) for value in data]
    if isinstance(data, (str, int, float, bool)) or data is None:
        return data
    return str(data)


def _mask_query_like_component(value: str) -> str:
    """保留 URL 参数名并掩码全部值，避免依赖不完备的凭据键名表。"""
    chunks = re.split(r"([&;])", value)
    for index in range(0, len(chunks), 2):
        segment = chunks[index]
        if not segment:
            continue
        raw_key, separator, _raw_value = segment.partition("=")
        chunks[index] = f"{raw_key}=******" if separator else "******"
    return "".join(chunks)


def _mask_referer(value: str) -> str:
    """保留 Referer URL 结构，但不保留查询、片段或用户信息中的凭据。"""
    before_fragment, fragment_separator, fragment = value.partition("#")
    if "?" in before_fragment:
        path, query = before_fragment.split("?", 1)
        before_fragment = f"{path}?{_mask_query_like_component(query)}"
    if fragment_separator:
        fragment = _mask_query_like_component(fragment)

    authority_match = re.match(
        r"^(?P<prefix>[a-zA-Z][a-zA-Z0-9+.-]*://)(?P<authority>[^/?#]*)(?P<suffix>.*)$",
        before_fragment,
    )
    if authority_match:
        authority = authority_match.group("authority")
        if "@" in authority:
            user_info, host = authority.rsplit("@", 1)
            username, separator, _password = user_info.partition(":")
            masked_user_info = f"{username}{separator or ':'}******"
            before_fragment = (
                f"{authority_match.group('prefix')}{masked_user_info}@{host}"
                f"{authority_match.group('suffix')}"
            )
    return before_fragment + (f"#{fragment}" if fragment_separator else "")


def _mask_forwarded_for(value: str) -> str:
    """仅保留合法 IP，避免把 X-Forwarded-For 当作任意字符串落库。"""
    masked_parts: list[str] = []
    for part in value.split(","):
        candidate = part.strip()
        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            masked_parts.append("******")
        else:
            masked_parts.append(candidate)
    return ", ".join(masked_parts)


def _sanitize_selected_header(name: str, value: str) -> str:
    if name == "referer":
        return _mask_referer(value)
    if name == "x-forwarded-for":
        return _mask_forwarded_for(value)
    return value


def _json_bytes(data: Any) -> bytes:
    return json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


def _trim_value(
    value: Any,
    string_limit: int,
    item_limit: int,
    depth: int = 0,
    priority_keys: tuple[str, ...] = (),
) -> Any:
    if depth > MAX_CONTEXT_DEPTH:
        return "***MAX_DEPTH***"
    if isinstance(value, str):
        return value if len(value) <= string_limit else value[:string_limit] + "...[TRUNCATED]"
    if isinstance(value, Mapping):
        items = list(value.items())
        if depth == 0 and priority_keys:
            priority_set = set(priority_keys)
            priority_items = [
                (key, item) for key, item in items if str(key) in priority_set
            ]
            priority_item_keys = {key for key, _item in priority_items}
            remaining_items = [
                (key, item) for key, item in items if key not in priority_item_keys
            ]
            selected_items = priority_items + remaining_items[:item_limit]
        else:
            selected_items = items[:item_limit]
        mapping_result = {
            str(key): _trim_value(item, string_limit, item_limit, depth + 1)
            for key, item in selected_items
        }
        if len(selected_items) < len(items):
            mapping_result["_truncated"] = True
        return mapping_result
    if isinstance(value, list):
        list_result = [
            _trim_value(item, string_limit, item_limit, depth + 1)
            for item in value[:item_limit]
        ]
        if len(value) > item_limit:
            list_result.append("...[TRUNCATED]")
        return list_result
    return value


def limit_request_context(context: Mapping[str, Any]) -> dict[str, Any]:
    """将结构化上下文限制在固定字节数内，并显式标记截断。"""
    original = copy.deepcopy(dict(context))
    original["truncated"] = bool(original.get("truncated", False))
    if len(_json_bytes(original)) <= MAX_REQUEST_CONTEXT_BYTES:
        return original

    for string_limit, item_limit in (
        (2048, 100),
        (1024, 50),
        (512, 25),
        (256, 10),
        (128, 5),
        (32, 2),
        (8, 1),
    ):
        candidate = _trim_value(
            original,
            string_limit,
            item_limit,
            priority_keys=_PRIORITY_CONTEXT_KEYS,
        )
        candidate["truncated"] = True
        if len(_json_bytes(candidate)) <= MAX_REQUEST_CONTEXT_BYTES:
            return candidate

    minimal: dict[str, Any] = {"truncated": True}
    for key in _PRIORITY_CONTEXT_KEYS:
        if key not in original:
            continue
        minimal[key] = _trim_value(original[key], 64, 5)
    if len(_json_bytes(minimal)) > MAX_REQUEST_CONTEXT_BYTES:
        minimal = {"truncated": True}
        for key in _PRIORITY_CONTEXT_KEYS:
            if key not in original:
                continue
            candidate = dict(minimal)
            candidate[key] = _trim_value(original[key], 8, 1)
            if len(_json_bytes(candidate)) <= MAX_REQUEST_CONTEXT_BYTES:
                minimal = candidate
    return minimal


def _query_values(query_params: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if hasattr(query_params, "multi_items"):
        pairs = query_params.multi_items()
    elif isinstance(query_params, Mapping):
        pairs = (
            (key, item)
            for key, values in query_params.items()
            for item in (values if isinstance(values, list) else [values])
        )
    else:
        return result
    grouped: dict[str, list[str]] = {}
    for key, value in pairs:
        grouped.setdefault(_to_camel(str(key)), []).append(str(value))
    for key, values in grouped.items():
        result[key] = values[0] if len(values) == 1 else values
    return mask_sensitive_data(result)


def serialize_query_params(query_params: Any) -> str:
    """将查询参数以可解析且已脱敏的 JSON 字符串保存。"""
    values = _query_values(query_params)
    if not values:
        return ""
    return json.dumps(values, ensure_ascii=False, separators=(",", ":"), default=str)


def _parse_multipart(raw_body: bytes, content_type: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """解析 multipart 的字段和文件摘要，不把文件内容写入上下文。"""
    envelope = (
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
        + raw_body
    )
    try:
        message = BytesParser(policy=email_policy).parsebytes(envelope)
    except Exception:  # noqa: BLE001 - 非标准 multipart 仍应保留主体哈希
        return {}, []

    body: dict[str, Any] = {}
    file_meta: list[dict[str, Any]] = []
    for part in message.walk():
        if part.is_multipart():
            continue
        params = dict(part.get_params(header="content-disposition", unquote=True) or [])
        field_name = str(params.get("name", ""))
        filename = params.get("filename")
        decoded_payload = part.get_payload(decode=True)
        payload = decoded_payload if isinstance(decoded_payload, bytes) else b""
        if filename is not None:
            file_meta.append(
                {
                    "fieldName": field_name,
                    "fileName": str(filename),
                    "contentType": part.get_content_type() or None,
                    "size": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            )
        elif field_name:
            try:
                value: Any = payload.decode(part.get_content_charset() or "utf-8")
            except (UnicodeDecodeError, LookupError):
                value = "[BINARY DATA]"
            if field_name in body:
                previous = body[field_name]
                body[field_name] = previous + [value] if isinstance(previous, list) else [previous, value]
            else:
                body[field_name] = value
    return _query_values(body), file_meta


def _request_may_have_body(
    request: Request,
    content_type: str,
    content_length_header: str | None,
) -> bool:
    """判断未知长度是否仍可能代表一个需要保护的请求体。"""
    if request.method.upper() not in _BODYLESS_METHODS:
        return True
    return bool(
        content_type
        or content_length_header is not None
        or request.headers.get("transfer-encoding")
    )


def get_body_capture_skip_info(request: Request) -> dict[str, Any] | None:
    """根据请求头决定是否可以在审计层读取完整 body。

    可能携带请求体的请求若没有可信的 Content-Length，也不能在进入业务端点前
    读取整包，否则会绕过审计采集的大小边界。无体方法在没有任何 body 信号时
    保留空 body 的既有处理方式。
    """
    content_type = request.headers.get("content-type", "").lower()
    content_length_header = request.headers.get("content-length")
    may_have_body = _request_may_have_body(
        request,
        content_type,
        content_length_header,
    )
    if content_length_header is None:
        if not may_have_body:
            return None
        return {
            "status": "skipped",
            "reason": "content-length-missing",
            "maxBytes": MAX_AUDIT_BODY_CAPTURE_BYTES,
        }

    try:
        content_length = int(content_length_header)
    except (TypeError, ValueError):
        if not may_have_body:
            return None
        return {
            "status": "skipped",
            "reason": "content-length-invalid",
            "maxBytes": MAX_AUDIT_BODY_CAPTURE_BYTES,
        }

    if content_length < 0:
        if not may_have_body:
            return None
        return {
            "status": "skipped",
            "reason": "content-length-invalid",
            "maxBytes": MAX_AUDIT_BODY_CAPTURE_BYTES,
        }

    if content_length <= MAX_AUDIT_BODY_CAPTURE_BYTES:
        return None
    return {
        "status": "skipped",
        "reason": "content-length-exceeds-limit",
        "contentLength": content_length,
        "maxBytes": MAX_AUDIT_BODY_CAPTURE_BYTES,
    }


def set_audit_object(
    request: Request,
    object_type: str,
    object_id: object,
    *,
    changed_fields: list[str] | tuple[str, ...] | None = None,
    **context: Any,
) -> None:
    """显式设置本次请求关联的业务对象，不从 URL 猜测对象。"""
    normalized_type = str(object_type or "").strip()[:MAX_OBJECT_TYPE_LENGTH]
    if not normalized_type:
        raise ValueError("object_type 不能为空")
    normalized_id = "" if object_id is None else str(object_id).strip()[:MAX_OBJECT_ID_LENGTH]
    request.state.audit_object = {"type": normalized_type, "id": normalized_id}
    audit_context = dict(getattr(request.state, "audit_context", {}) or {})
    normalized_changed_fields = get_changed_fields(changed_fields)
    request.state.audit_changed_fields = normalized_changed_fields
    audit_context["changedFields"] = normalized_changed_fields
    for key, value in context.items():
        normalized_key = _to_camel(str(key))
        if normalized_key not in _RESERVED_CONTEXT_KEYS:
            audit_context[normalized_key] = value
    request.state.audit_context = mask_sensitive_data(audit_context)


def set_audit_context(request: Request, **context: Any) -> None:
    """补充当前请求的结构化审计上下文。"""
    audit_context = dict(getattr(request.state, "audit_context", {}) or {})
    for key, value in context.items():
        normalized_key = _to_camel(str(key))
        if normalized_key not in _RESERVED_CONTEXT_KEYS:
            audit_context[normalized_key] = value
    request.state.audit_context = mask_sensitive_data(audit_context)


def get_audit_object(request: Request) -> dict[str, str] | None:
    """读取显式设置的对象关联。"""
    value = getattr(request.state, "audit_object", None)
    if not isinstance(value, Mapping):
        return None
    return {"type": str(value.get("type", "")), "id": str(value.get("id", ""))}


async def build_request_context(request: Request) -> dict[str, Any]:
    """采集路径、查询、请求体、白名单 Header 和文件元数据。"""
    body_capture = get_body_capture_skip_info(request)
    if body_capture is None:
        try:
            raw_body = await request.body()
        except Exception:  # noqa: BLE001 - 已被消费的请求体不能阻断审计
            raw_body = b""
            body_capture = {
                "status": "unavailable",
                "reason": "stream-consumed",
            }
    else:
        raw_body = b""

    content_type = request.headers.get("content-type", "")
    body: Any = {}
    file_meta: list[dict[str, Any]] = []
    lowered_content_type = content_type.lower()
    if raw_body and "application/json" in lowered_content_type:
        try:
            body = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, TypeError, ValueError):
            body = {"_invalid": True}
    elif raw_body and "multipart/form-data" in lowered_content_type:
        body, file_meta = _parse_multipart(raw_body, content_type)
    elif raw_body and "application/x-www-form-urlencoded" in lowered_content_type:
        body = _query_values(parse_qs(raw_body.decode("utf-8", errors="replace"), keep_blank_values=True))

    headers: dict[str, str] = {}
    for input_name, output_name in _SELECTED_HEADERS.items():
        value = request.headers.get(input_name)
        if value is None or value == "":
            continue
        headers[output_name] = _sanitize_selected_header(output_name, value)
    audit_context = getattr(request.state, "audit_context", {}) or {}
    changed_fields = getattr(request.state, "audit_changed_fields", None)
    if changed_fields is None:
        changed_fields = list(audit_context.get("changedFields", []))
    context: dict[str, Any] = {
        "pathParams": {
            _to_camel(str(key)): str(value)
            for key, value in (getattr(request, "path_params", {}) or {}).items()
        },
        "query": _query_values(request.query_params),
        "body": mask_sensitive_data(body),
        "selectedHeaders": headers,
        "fileMeta": file_meta,
        "changedFields": list(changed_fields),
        "bodyHash": hashlib.sha256(raw_body).hexdigest() if raw_body else "",
    }
    if body_capture is not None:
        context["bodyCapture"] = body_capture
        if body_capture.get("status") == "skipped":
            context["truncated"] = True
    object_info = get_audit_object(request)
    if object_info:
        context["objectType"] = object_info["type"]
        context["objectId"] = object_info["id"]
    context.update(
        {
            key: value
            for key, value in mask_sensitive_data(
                audit_context
            ).items()
            if key not in _RESERVED_CONTEXT_KEYS
        }
    )
    return limit_request_context(context)


__all__ = [
    "MAX_AUDIT_BODY_CAPTURE_BYTES",
    "MAX_OBJECT_ID_LENGTH",
    "MAX_OBJECT_TYPE_LENGTH",
    "MAX_REQUEST_CONTEXT_BYTES",
    "build_request_context",
    "get_body_capture_skip_info",
    "get_changed_fields",
    "get_audit_object",
    "limit_request_context",
    "mask_sensitive_data",
    "serialize_query_params",
    "set_audit_context",
    "set_audit_object",
]
