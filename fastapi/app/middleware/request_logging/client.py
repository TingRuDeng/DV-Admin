"""
请求客户端信息解析

提取客户端 IP 与 User-Agent 信息，供请求日志中间件复用。
"""

from fastapi import Request

from app.core.config import settings
from app.core.login_throttle_policy import trusted_client_ip


def get_client_ip(request: Request) -> str:
    """日志与登录保护使用相同的受信代理边界。"""
    return trusted_client_ip(
        request.client.host if request.client else "",
        request.headers.get("X-Forwarded-For", ""),
        settings.trusted_proxy_ips,
    )


def parse_user_agent(user_agent: str) -> dict[str, str]:
    """解析 User-Agent 的浏览器、操作系统和设备类型。"""
    result = {
        "browser": "Unknown",
        "os": "Unknown",
        "device": "Unknown",
    }

    if not user_agent:
        return result

    user_agent_lower = user_agent.lower()
    result["browser"] = _parse_browser(user_agent_lower)
    result["os"] = _parse_os(user_agent_lower)
    result["device"] = _parse_device(user_agent_lower)
    return result


def _parse_browser(user_agent_lower: str) -> str:
    """解析浏览器名称。"""
    if "edg/" in user_agent_lower:
        return "Edge"
    if "chrome/" in user_agent_lower:
        return "Chrome"
    if "firefox/" in user_agent_lower:
        return "Firefox"
    if "safari/" in user_agent_lower and "chrome/" not in user_agent_lower:
        return "Safari"
    if "opera/" in user_agent_lower or "opr/" in user_agent_lower:
        return "Opera"
    if "msie" in user_agent_lower or "trident/" in user_agent_lower:
        return "IE"
    return "Unknown"


def _parse_os(user_agent_lower: str) -> str:
    """解析操作系统名称。"""
    if "windows" in user_agent_lower:
        return "Windows"
    if "mac" in user_agent_lower:
        return "MacOS"
    if "linux" in user_agent_lower:
        return "Linux"
    if "android" in user_agent_lower:
        return "Android"
    if "iphone" in user_agent_lower or "ipad" in user_agent_lower:
        return "iOS"
    return "Unknown"


def _parse_device(user_agent_lower: str) -> str:
    """解析设备类型。"""
    if (
        "mobile" in user_agent_lower
        or "android" in user_agent_lower
        or "iphone" in user_agent_lower
    ):
        return "Mobile"
    if "tablet" in user_agent_lower or "ipad" in user_agent_lower:
        return "Tablet"
    return "Desktop"
