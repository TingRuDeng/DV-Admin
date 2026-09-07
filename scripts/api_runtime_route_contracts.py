"""Framework-independent registry for all deployed business HTTP routes."""

from __future__ import annotations

import re
from dataclasses import dataclass

from scripts.api_endpoint_contracts import iter_critical_endpoint_contracts

# Implicit HEAD/OPTIONS and these process/framework endpoints are not business APIs.
EXCLUDED_METHODS = {"HEAD", "OPTIONS"}
EXCLUDED_PATHS = {
    "/",
    "/health",
    "/health/live",
    "/health/ready",
    "/health/detailed",
    "/api/swagger",
    "/api/redoc",
    "/api/openapi.json",
    "/api/v1/swagger",
    "/api/v1/swagger{}",
    "/api/v1/redoc",
    "/docs/oauth2-redirect",
}


@dataclass(frozen=True)
class RouteRegistration:
    method: str
    path: str
    backends: tuple[str, ...]
    kind: str
    reason: str


BOTH = ("django", "fastapi")
DJANGO = ("django",)
FASTAPI = ("fastapi",)

# Explicitly reviewed supplements to the critical endpoint catalog, not auto-discovery.
SUPPLEMENTAL_ROUTES = (
    *(
        RouteRegistration(
            "DELETE",
            f"/api/v1/system/{resource}/{{id}}",
            BOTH,
            "shared",
            "single-resource deletion",
        )
        for resource in (
            "departments",
            "dict-items",
            "dicts",
            "logs",
            "notices",
            "roles",
            "users",
        )
    ),
    RouteRegistration(
        "DELETE", "/api/v1/system/logs/clear/{days}", BOTH, "shared", "audit retention"
    ),
    *(
        RouteRegistration(
            "GET",
            f"/api/v1/system/{resource}/{{id}}",
            BOTH,
            "shared",
            "resource detail",
        )
        for resource in ("departments", "dicts", "menus")
    ),
    *(
        RouteRegistration(
            "GET",
            f"/api/v1/system/{resource}/options",
            BOTH,
            "shared",
            "selector options",
        )
        for resource in ("menus", "roles", "users")
    ),
    *(
        RouteRegistration(
            "GET", f"/api/v1/system/logs/{action}", BOTH, "shared", "audit aggregates"
        )
        for action in ("visit-stats", "visit-trend")
    ),
    *(
        RouteRegistration(
            "POST", f"/api/v1/oauth/{action}", BOTH, "shared", "session lifecycle"
        )
        for action in ("logout", "refresh-token")
    ),
    RouteRegistration(
        "PATCH", "/api/v1/system/users/{id}", BOTH, "compat", "legacy partial update"
    ),
    RouteRegistration(
        "DELETE", "/api/v1/system/menus", DJANGO, "compat", "legacy JSON batch delete"
    ),
    RouteRegistration(
        "GET", "/api/v1/oauth/home", DJANGO, "backend_only", "legacy dashboard data"
    ),
    RouteRegistration(
        "GET",
        "/api/v1/system/dict-items/{id}",
        DJANGO,
        "backend_only",
        "DRF item detail",
    ),
    RouteRegistration(
        "GET",
        "/api/v1/system/users/{id}/permissions",
        DJANGO,
        "backend_only",
        "user permission ID lookup",
    ),
    *(
        RouteRegistration(
            "PATCH",
            f"/api/v1/system/{resource}/{{id}}",
            DJANGO,
            "compat",
            "DRF partial update",
        )
        for resource in ("departments", "dict-items", "dicts", "menus", "roles")
    ),
    RouteRegistration(
        "PATCH",
        "/api/v1/system/users/{id}/password/reset",
        DJANGO,
        "compat",
        "legacy reset method",
    ),
    *(
        RouteRegistration(
            "PUT",
            f"/api/v1/information/{action}",
            DJANGO,
            "compat",
            "legacy profile alias",
        )
        for action in ("change-information", "change-password")
    ),
    RouteRegistration(
        "GET", "/api/v1/oauth/captcha", FASTAPI, "backend_only", "captcha challenge"
    ),
    RouteRegistration(
        "GET",
        "/api/v1/system/departments/options",
        FASTAPI,
        "backend_only",
        "department selector",
    ),
    RouteRegistration(
        "GET",
        "/api/v1/system/menus/perms",
        FASTAPI,
        "backend_only",
        "permission-code enumeration",
    ),
    RouteRegistration(
        "GET",
        "/api/v1/system/dicts/code/{code}",
        FASTAPI,
        "backend_only",
        "dictionary code lookup",
    ),
    RouteRegistration(
        "GET",
        "/api/v1/system/roles/{id}/menus",
        FASTAPI,
        "compat",
        "legacy menu lookup",
    ),
    RouteRegistration(
        "POST", "/api/v1/oauth/token", FASTAPI, "compat", "OAuth password form login"
    ),
    RouteRegistration(
        "POST",
        "/api/v1/system/users/{id}/password/reset",
        FASTAPI,
        "compat",
        "legacy reset method",
    ),
    *(
        RouteRegistration(
            method,
            f"/api/v1/system/dicts/{{id}}/items{suffix}",
            FASTAPI,
            "compat",
            "legacy nested dictionary item route",
        )
        for method, suffix in (
            ("GET", ""),
            ("POST", ""),
            ("PUT", "/{item_id}"),
            ("DELETE", "/{item_id}"),
        )
    ),
)


def normalize_path(path: str) -> str:
    path = re.sub(r"\(\?P<[^>]+>[^)]+\)", "{}", path)
    path = re.sub(r"<[^>]+>|\{[^}]*\}", "{}", path)
    path = path.replace("^", "").removesuffix("\\Z").removesuffix("$")
    path = path.replace("\\.", ".")
    assert not any(char in path for char in "()?[]\\<>"), f"Unnormalized route: {path}"
    return "/" + path.strip("/") if path.strip("/") else "/"


def expected_routes(backend: str) -> set[tuple[str, str]]:
    assert backend in {"django", "fastapi"}
    return {
        (contract.method, normalize_path(contract.path))
        for contract in iter_critical_endpoint_contracts()
    } | {
        (entry.method, normalize_path(entry.path))
        for entry in SUPPLEMENTAL_ROUTES
        if backend in entry.backends
    }


def assert_runtime_route_registry() -> None:
    seen = {
        backend: {
            (entry.method, normalize_path(entry.path))
            for entry in iter_critical_endpoint_contracts()
        }
        for backend in BOTH
    }
    for entry in SUPPLEMENTAL_ROUTES:
        assert entry.method in {"GET", "POST", "PUT", "PATCH", "DELETE"}, entry
        assert entry.path.startswith("/api/v1/") and entry.reason, entry
        assert entry.kind in {"shared", "backend_only", "compat"}, entry
        assert entry.backends in (BOTH, DJANGO, FASTAPI), entry
        assert entry.kind != "shared" or entry.backends == BOTH, entry
        assert entry.kind != "backend_only" or len(entry.backends) == 1, entry
        for backend in entry.backends:
            route = (entry.method, normalize_path(entry.path))
            assert route not in seen[backend], f"Duplicate route: {backend} {route}"
            seen[backend].add(route)


def assert_runtime_routes(backend: str, routes: set[tuple[str, str]]) -> None:
    assert_runtime_route_registry()
    normalized = {(method.upper(), normalize_path(path)) for method, path in routes}
    actual = set()
    for method, path in normalized:
        if path in EXCLUDED_PATHS:
            continue
        if method == "HEAD" and ("GET", path) in normalized:
            continue
        if method == "OPTIONS" and any(
            m not in EXCLUDED_METHODS and p == path for m, p in normalized
        ):
            continue
        actual.add((method, path))
    expected = expected_routes(backend)
    unregistered = sorted(actual - expected)
    missing = sorted(expected - actual)
    assert (
        not unregistered and not missing
    ), f"{backend}: unregistered routes={unregistered}; missing registered routes={missing}"
