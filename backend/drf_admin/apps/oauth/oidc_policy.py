"""Shared OIDC policy; keep the two packaged backend copies byte-identical."""

import base64
import hashlib
import hmac
import json
import re
import secrets
from urllib.parse import quote_plus, urlencode, urlsplit

import jwt

STATE_TTL_SECONDS = 600
HTTP_TIMEOUT_SECONDS = 5
METADATA_CACHE_SECONDS = 3600
CLOCK_SKEW_SECONDS = 60
STATE_KEY_PREFIX = "oidc:state:"
DEFAULT_SCOPES = "openid profile email"
SUPPORTED_SIGNING_ALGORITHMS = ("RS256", "ES256", "PS256")
ISSUER_MAX_LENGTH = 255
SUBJECT_MAX_LENGTH = 255
EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 20
USERNAME_MAX_LENGTH = 150

MESSAGE_DISABLED = "未启用单点登录"
MESSAGE_FLOW_INVALID = "登录状态无效或已过期，请重新发起单点登录"
MESSAGE_PROVIDER_FAILED = "身份提供方校验失败"
MESSAGE_NOT_PROVISIONED = "该账号未开通，请联系管理员"
MESSAGE_EMAIL_AMBIGUOUS = "该邮箱对应多个本地账号，请联系管理员"
MESSAGE_USER_DISABLED = "用户已被禁用，请联系管理员"

_USERNAME_PATTERN = re.compile(r"^[\w.@+-]+\Z")
_MOBILE_PATTERN = re.compile(r"^1[3-9]\d{9}$")
_SETTING_SEPARATOR = re.compile(r"[\s,]+")


class OidcError(Exception):
    """单点登录失败；message 可以直接返回给前端。"""

    def __init__(self, message: str = MESSAGE_PROVIDER_FAILED):
        super().__init__(message)
        self.message = message


class UnknownSigningKey(OidcError):
    """ID Token 的 kid 不在当前 JWKS 中，调用方应强制刷新一次 JWKS 后重试。"""


def random_secret() -> str:
    return secrets.token_urlsafe(32)


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def pkce_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def state_key(state: str) -> str:
    return STATE_KEY_PREFIX + sha256_hex(state)


def start_flow() -> dict[str, str]:
    """生成一次登录流程的随机值；record 存入 Redis，flow_secret 只返回给发起方。"""
    state = random_secret()
    nonce = random_secret()
    code_verifier = random_secret()
    flow_secret = random_secret()
    record = json.dumps(
        {
            "nonce": nonce,
            "codeVerifier": code_verifier,
            "flowSecretHash": sha256_hex(flow_secret),
        },
        separators=(",", ":"),
    )
    return {
        "state": state,
        "nonce": nonce,
        "code_verifier": code_verifier,
        "flow_secret": flow_secret,
        "record": record,
    }


def read_flow_record(raw: object, flow_secret: str) -> dict[str, str]:
    """解析已原子取出的 state 记录，并确认请求方持有发起时下发的 flowSecret。"""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if not isinstance(raw, str):
        raise OidcError(MESSAGE_FLOW_INVALID)
    try:
        record = json.loads(raw)
    except ValueError as error:
        raise OidcError(MESSAGE_FLOW_INVALID) from error
    fields = ("nonce", "codeVerifier", "flowSecretHash")
    if not isinstance(record, dict) or not all(isinstance(record.get(k), str) for k in fields):
        raise OidcError(MESSAGE_FLOW_INVALID)
    presented = sha256_hex(flow_secret) if isinstance(flow_secret, str) else ""
    if not hmac.compare_digest(record["flowSecretHash"], presented):
        raise OidcError(MESSAGE_FLOW_INVALID)
    return record


def split_setting(value: str) -> list[str]:
    return [item for item in _SETTING_SEPARATOR.split(value or "") if item]


def normalized_scopes(value: str) -> str:
    scopes = split_setting(value) or split_setting(DEFAULT_SCOPES)
    if "openid" not in scopes:
        scopes.insert(0, "openid")
    return " ".join(dict.fromkeys(scopes))


def settings_errors(issuer: str, client_id: str, redirect_uri: str, production: bool) -> list[str]:
    """启用单点登录时的配置检查；生产环境要求 issuer 和回调地址使用 https。"""
    errors = []
    required = (
        ("OIDC_ISSUER", issuer),
        ("OIDC_CLIENT_ID", client_id),
        ("OIDC_REDIRECT_URI", redirect_uri),
    )
    for name, value in required:
        if not value:
            errors.append(f"{name} 未配置")
    if production:
        for name, value in (("OIDC_ISSUER", issuer), ("OIDC_REDIRECT_URI", redirect_uri)):
            if value and urlsplit(value).scheme != "https":
                errors.append(f"{name} 在生产环境必须使用 https")
    return errors


def discovery_url(issuer: str) -> str:
    return issuer.rstrip("/") + "/.well-known/openid-configuration"


def _require_url(value: object, secure: bool) -> None:
    if not isinstance(value, str):
        raise OidcError()
    parts = urlsplit(value)
    if parts.scheme not in ("https", "http") or not parts.netloc:
        raise OidcError()
    if secure and parts.scheme != "https":
        raise OidcError()


def signing_algorithms(discovery: dict) -> list[str]:
    advertised = discovery.get("id_token_signing_alg_values_supported") or ["RS256"]
    return [algorithm for algorithm in SUPPORTED_SIGNING_ALGORITHMS if algorithm in advertised]


def validate_discovery(document: object, expected_issuer: str) -> dict:
    """discovery 的 issuer 必须与配置逐字符相等，端点协议不得低于 issuer。"""
    if not isinstance(document, dict) or document.get("issuer") != expected_issuer:
        raise OidcError()
    if len(expected_issuer) > ISSUER_MAX_LENGTH:
        raise OidcError()
    secure = urlsplit(expected_issuer).scheme == "https"
    for key in ("authorization_endpoint", "token_endpoint", "jwks_uri"):
        _require_url(document.get(key), secure)
    response_types = document.get("response_types_supported")
    if isinstance(response_types, list) and "code" not in response_types:
        raise OidcError()
    challenge_methods = document.get("code_challenge_methods_supported")
    if isinstance(challenge_methods, list) and "S256" not in challenge_methods:
        raise OidcError()
    if not signing_algorithms(document):
        raise OidcError()
    return document


def token_endpoint_auth_method(discovery: dict, has_client_secret: bool) -> str:
    if not has_client_secret:
        return "none"
    supported = discovery.get("token_endpoint_auth_methods_supported") or ["client_secret_basic"]
    for method in ("client_secret_basic", "client_secret_post"):
        if method in supported:
            return method
    raise OidcError()


def authorization_url(
    discovery: dict,
    client_id: str,
    redirect_uri: str,
    scopes: str,
    state: str,
    nonce: str,
    code_verifier: str,
) -> str:
    query = urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": normalized_scopes(scopes),
            "state": state,
            "nonce": nonce,
            "code_challenge": pkce_challenge(code_verifier),
            "code_challenge_method": "S256",
        }
    )
    endpoint = discovery["authorization_endpoint"]
    separator = "&" if "?" in endpoint else "?"
    return endpoint + separator + query


def token_request(
    discovery: dict,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    code: str,
    code_verifier: str,
) -> tuple[str, dict[str, str], dict[str, str]]:
    """返回 (url, form, headers)，调用方以表单 POST 且不跟随重定向。"""
    method = token_endpoint_auth_method(discovery, bool(client_secret))
    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    headers = {"Accept": "application/json"}
    if method == "client_secret_basic":
        credentials = f"{quote_plus(client_id)}:{quote_plus(client_secret)}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {encoded}"
    else:
        form["client_id"] = client_id
        if method == "client_secret_post":
            form["client_secret"] = client_secret
    return discovery["token_endpoint"], form, headers


def id_token_from_response(payload: object) -> str:
    if not isinstance(payload, dict) or not isinstance(payload.get("id_token"), str):
        raise OidcError()
    return payload["id_token"]


def check_response_issuer(discovery: dict, iss: object) -> None:
    """RFC 9207：回调带了 iss 就必须一致；提供方声明支持时必须带上。"""
    if iss:
        if iss != discovery["issuer"]:
            raise OidcError()
    elif discovery.get("authorization_response_iss_parameter_supported") is True:
        raise OidcError()


def _select_signing_key(jwks: object, header: dict) -> dict:
    keys = jwks.get("keys") if isinstance(jwks, dict) else None
    if not isinstance(keys, list):
        raise OidcError()
    kid = header.get("kid")
    candidates = [
        key
        for key in keys
        if isinstance(key, dict)
        and key.get("use", "sig") == "sig"
        and (kid is None or key.get("kid") == kid)
    ]
    if not candidates:
        raise UnknownSigningKey()
    if kid is None and len(candidates) != 1:
        raise OidcError()
    return candidates[0]


def verify_id_token(
    id_token: str, jwks: object, discovery: dict, client_id: str, nonce: str
) -> dict:
    """校验签名、iss、aud、azp、exp、iat 和 nonce；只接受非对称签名算法。"""
    try:
        header = jwt.get_unverified_header(id_token)
    except jwt.PyJWTError as error:
        raise OidcError() from error
    algorithm = header.get("alg")
    if algorithm not in signing_algorithms(discovery):
        raise OidcError()
    jwk = _select_signing_key(jwks, header)
    if jwk.get("alg") not in (None, algorithm):
        raise OidcError()
    try:
        signing_key = jwt.PyJWK(jwk, algorithm=algorithm)
        claims = jwt.decode(
            id_token,
            key=signing_key.key,
            algorithms=[algorithm],
            audience=client_id,
            issuer=discovery["issuer"],
            leeway=CLOCK_SKEW_SECONDS,
            options={"require": ["iss", "sub", "aud", "exp", "iat"]},
        )
    except (jwt.PyJWTError, ValueError, TypeError) as error:
        raise OidcError() from error
    audiences = claims["aud"] if isinstance(claims["aud"], list) else [claims["aud"]]
    authorized_party = claims.get("azp")
    if len(audiences) > 1 and authorized_party is None:
        raise OidcError()
    if authorized_party is not None and authorized_party != client_id:
        raise OidcError()
    token_nonce = claims.get("nonce")
    if not isinstance(token_nonce, str) or not hmac.compare_digest(token_nonce, nonce):
        raise OidcError()
    subject = claims["sub"]
    if not isinstance(subject, str) or not subject or len(subject) > SUBJECT_MAX_LENGTH:
        raise OidcError()
    return claims


def _claim_text(claims: dict, name: str) -> str:
    value = claims.get(name)
    return value.strip() if isinstance(value, str) else ""


def profile_from_claims(claims: dict) -> dict:
    """把 ID Token claims 映射为本地账号资料；邮箱统一小写，姓名截断到本地字段长度。"""
    email = _claim_text(claims, "email").lower()
    if len(email) > EMAIL_MAX_LENGTH or email.count("@") != 1:
        email = ""
    preferred_username = _claim_text(claims, "preferred_username")
    name = _claim_text(claims, "name") or preferred_username or email.split("@")[0]
    return {
        "subject": claims["sub"],
        "email": email,
        "email_verified": bool(email) and claims.get("email_verified") in (True, "true"),
        "name": name[:NAME_MAX_LENGTH],
        "preferred_username": preferred_username,
    }


def is_acceptable_username(value: str) -> bool:
    """与本地用户名规则一致：不能为空、纯数字或像手机号，只含字母数字和 .@+-_。"""
    return (
        0 < len(value) <= USERNAME_MAX_LENGTH
        and bool(_USERNAME_PATTERN.match(value))
        and not value.isdigit()
        and not _MOBILE_PATTERN.match(value)
    )


def username_candidates(profile: dict, issuer: str) -> list[str]:
    """按优先级给出候选用户名，调用方取第一个未被占用的；最后两项由身份哈希保证唯一。"""
    digest = sha256_hex(f"{issuer}|{profile['subject']}")
    bases = [
        base
        for base in (profile["preferred_username"], profile["email"].split("@")[0])
        if is_acceptable_username(base)
    ]
    suffixed = [f"{base[: USERNAME_MAX_LENGTH - 7]}_{digest[:6]}" for base in bases]
    fallbacks = [f"oidc_{digest[:12]}", f"oidc_{digest[:32]}"]
    return list(dict.fromkeys(bases + suffixed + fallbacks))


def email_domain_allowed(profile: dict, allowed_domains: list[str]) -> bool:
    """未配置域名白名单时不限制；配置后只接受已验证且域名在列表内的邮箱。"""
    if not allowed_domains:
        return True
    if not profile["email_verified"]:
        return False
    domain = profile["email"].rsplit("@", 1)[-1]
    return domain in {item.lower() for item in allowed_domains}
