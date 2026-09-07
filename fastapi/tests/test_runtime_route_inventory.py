import pytest
from fastapi import FastAPI
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from app.main import create_app
from scripts.api_runtime_route_contracts import assert_runtime_routes


def registered_routes(app, prefix=""):
    routes = set()
    for route in app.routes:
        if isinstance(route, Mount):
            if route.path == "/media" and isinstance(route.app, StaticFiles):
                continue
            routes.update(registered_routes(route.app, prefix + route.path))
        else:
            methods = getattr(route, "methods", None)
            assert methods is not None, f"Unsupported route type: {route}"
            routes.update((method, prefix + route.path) for method in methods)
    return routes


def test_all_actual_fastapi_business_routes_are_registered():
    assert_runtime_routes("fastapi", registered_routes(create_app()))


def test_new_nested_router_cannot_escape_inventory():
    app = create_app()
    nested = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @nested.get("/new-business")
    def new_business():
        return {}

    app.mount("/new-module", nested)
    with pytest.raises(AssertionError, match="/new-module/new-business"):
        assert_runtime_routes("fastapi", registered_routes(app))
