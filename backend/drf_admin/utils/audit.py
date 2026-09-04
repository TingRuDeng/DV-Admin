# -*- coding: utf-8 -*-
"""审计日志请求上下文与业务对象关联 helper。"""

from __future__ import annotations

import copy
import hashlib
import ipaddress
import json
import re
from collections.abc import Mapping
from typing import Any

from django.http import HttpRequest

MAX_REQUEST_CONTEXT_BYTES = 16 * 1024
MAX_OBJECT_TYPE_LENGTH = 100
MAX_OBJECT_ID_LENGTH = 255
MAX_CONTEXT_DEPTH = 10

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
        "objectType",
        "objectId",
        "truncated",
    }
)
_PRIORITY_CONTEXT_KEYS = (
    "objectType",
    "objectId",
    "bodyHash",
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
    "CONTENT_TYPE": "content-type",
    "HTTP_ACCEPT": "accept",
    "HTTP_USER_AGENT": "user-agent",
    "HTTP_X_REQUEST_ID": "x-request-id",
    "HTTP_X_FORWARDED_FOR": "x-forwarded-for",
    "HTTP_REFERER": "referer",
}


def _normalise_key(key: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


def _is_sensitive_key(key: object) -> bool:
    normalised = _normalise_key(key)
    return any(keyword in normalised for keyword in _SENSITIVE_KEYWORDS)


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

    # URL 中的 basic-auth 密码同样属于请求凭据，隐藏密码而保留主机定位信息。
    authority_match = re.match(r"^(?P<prefix>[a-zA-Z][a-zA-Z0-9+.-]*://)(?P<authority>[^/?#]*)(?P<suffix>.*)$", before_fragment)
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
        if len(value) <= string_limit:
            return value
        return value[:string_limit] + "...[TRUNCATED]"
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
        result = {
            str(key): _trim_value(item, string_limit, item_limit, depth + 1)
            for key, item in selected_items
        }
        if len(selected_items) < len(items):
            result["_truncated"] = True
        return result
    if isinstance(value, list):
        result = [_trim_value(item, string_limit, item_limit, depth + 1) for item in value[:item_limit]]
        if len(value) > item_limit:
            result.append("...[TRUNCATED]")
        return result
    return value


def limit_request_context(context: Mapping[str, Any]) -> dict[str, Any]:
    """将结构化上下文限制在固定字节数内，并显式标记截断。"""
    original = copy.deepcopy(dict(context))
    original["truncated"] = False
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

    # 极端情况下（例如拥有数千个不同顶层字段）保留合法且可识别的最小结构。
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


def _query_values(query_dict: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if hasattr(query_dict, "lists"):
        pairs = query_dict.lists()
    elif isinstance(query_dict, Mapping):
        pairs = ((key, value if isinstance(value, list) else [value]) for key, value in query_dict.items())
    else:
        return result
    for key, values in pairs:
        values = [str(value) for value in values]
        result[_to_camel(str(key))] = values[0] if len(values) == 1 else values
    return mask_sensitive_data(result)


def serialize_query_params(query_dict: Any) -> str:
    """将查询参数以可解析且已脱敏的 JSON 字符串保存。"""
    values = _query_values(query_dict)
    if not values:
        return ""
    return json.dumps(values, ensure_ascii=False, separators=(",", ":"), default=str)


def _read_uploaded_file(uploaded_file: Any) -> tuple[int, str]:
    file_obj = getattr(uploaded_file, "file", uploaded_file)
    original_position = None
    try:
        original_position = file_obj.tell()
    except (AttributeError, OSError):
        pass
    digest = hashlib.sha256()
    size = 0
    try:
        if hasattr(uploaded_file, "chunks"):
            for chunk in uploaded_file.chunks():
                digest.update(chunk)
                size += len(chunk)
        else:
            while True:
                chunk = file_obj.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                size += len(chunk)
    finally:
        if original_position is not None:
            try:
                file_obj.seek(original_position)
            except (AttributeError, OSError):
                pass
    return size, digest.hexdigest()


def _file_metadata(files: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if not hasattr(files, "lists"):
        return result
    for field_name, values in files.lists():
        for uploaded_file in values:
            size, digest = _read_uploaded_file(uploaded_file)
            result.append(
                {
                    "fieldName": str(field_name),
                    "fileName": str(getattr(uploaded_file, "name", "")),
                    "contentType": str(getattr(uploaded_file, "content_type", "")) or None,
                    "size": size,
                    "sha256": digest,
                }
            )
    return result


def set_audit_object(
    request: HttpRequest,
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
    object_value = {"type": normalized_type, "id": normalized_id}
    request.audit_object = object_value
    # DRF wraps Django's HttpRequest; middleware receives the underlying request.
    wrapped_request = getattr(request, "_request", None)
    if wrapped_request is not None:
        wrapped_request.audit_object = object_value
    audit_context = dict(getattr(request, "audit_context", {}) or {})
    if wrapped_request is not None:
        audit_context.update(getattr(wrapped_request, "audit_context", {}) or {})
    normalized_changed_fields = get_changed_fields(changed_fields)
    request.audit_changed_fields = normalized_changed_fields
    if wrapped_request is not None:
        wrapped_request.audit_changed_fields = normalized_changed_fields
    audit_context["changedFields"] = normalized_changed_fields
    for key, value in context.items():
        normalized_key = _to_camel(str(key))
        if normalized_key not in _RESERVED_CONTEXT_KEYS:
            audit_context[normalized_key] = value
    masked_context = mask_sensitive_data(audit_context)
    request.audit_context = masked_context
    if wrapped_request is not None:
        wrapped_request.audit_context = masked_context


def set_audit_context(request: HttpRequest, **context: Any) -> None:
    """补充当前请求的结构化审计上下文。"""
    wrapped_request = getattr(request, "_request", None)
    audit_context = dict(getattr(request, "audit_context", {}) or {})
    if wrapped_request is not None:
        audit_context.update(getattr(wrapped_request, "audit_context", {}) or {})
    for key, value in context.items():
        normalized_key = _to_camel(str(key))
        if normalized_key not in _RESERVED_CONTEXT_KEYS:
            audit_context[normalized_key] = value
    masked_context = mask_sensitive_data(audit_context)
    request.audit_context = masked_context
    if wrapped_request is not None:
        wrapped_request.audit_context = masked_context


def get_audit_object(request: HttpRequest) -> dict[str, str] | None:
    """读取显式设置的对象关联。"""
    value = getattr(request, "audit_object", None)
    if value is None:
        value = getattr(getattr(request, "_request", None), "audit_object", None)
    if not isinstance(value, Mapping):
        return None
    return {
        "type": str(value.get("type", "")),
        "id": str(value.get("id", "")),
    }


def build_request_context(request: HttpRequest) -> dict[str, Any]:
    """采集路径、查询、请求体、白名单 Header 和文件元数据。"""
    raw_body = b""
    try:
        raw_body = request.body or b""
    except Exception:  # noqa: BLE001 - 已被消费的请求体不能阻断审计
        raw_body = b""

    body: Any = {}
    content_type = str(request.META.get("CONTENT_TYPE", ""))
    if raw_body and "application/json" in content_type:
        try:
            body = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, TypeError, ValueError):
            body = {"_invalid": True}
    elif getattr(request, "POST", None):
        body = _query_values(request.POST)

    resolver_match = getattr(request, "resolver_match", None)
    raw_path_params = getattr(resolver_match, "kwargs", {}) if resolver_match else {}
    path_params = {
        _to_camel(str(key)): str(value)
        for key, value in raw_path_params.items()
    }
    headers = {
        output_name: _sanitize_selected_header(output_name, str(request.META[input_name]))
        for input_name, output_name in _SELECTED_HEADERS.items()
        if request.META.get(input_name) not in (None, "")
    }
    audit_context = getattr(request, "audit_context", None)
    if audit_context is None:
        audit_context = getattr(getattr(request, "_request", None), "audit_context", {})
    changed_fields = getattr(request, "audit_changed_fields", None)
    if changed_fields is None:
        changed_fields = getattr(getattr(request, "_request", None), "audit_changed_fields", None)
    if changed_fields is None:
        changed_fields = list((audit_context or {}).get("changedFields", []))
    context: dict[str, Any] = {
        "pathParams": path_params,
        "query": _query_values(request.GET),
        "body": mask_sensitive_data(body),
        "selectedHeaders": headers,
        "fileMeta": _file_metadata(getattr(request, "FILES", {})),
        "changedFields": list(changed_fields),
        "bodyHash": hashlib.sha256(raw_body).hexdigest() if raw_body else "",
    }
    object_info = get_audit_object(request)
    if object_info:
        context["objectType"] = object_info["type"]
        context["objectId"] = object_info["id"]
    context.update(
        {
            key: value
            for key, value in mask_sensitive_data(audit_context or {}).items()
            if key not in _RESERVED_CONTEXT_KEYS
        }
    )
    return limit_request_context(context)


__all__ = [
    "MAX_OBJECT_ID_LENGTH",
    "MAX_OBJECT_TYPE_LENGTH",
    "MAX_REQUEST_CONTEXT_BYTES",
    "build_request_context",
    "get_changed_fields",
    "get_audit_object",
    "limit_request_context",
    "mask_sensitive_data",
    "serialize_query_params",
    "set_audit_context",
    "set_audit_object",
]
