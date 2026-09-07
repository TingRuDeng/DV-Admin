import pytest
from django.urls import URLResolver, get_resolver, include, path
from rest_framework.views import APIView
from scripts.api_runtime_route_contracts import (
    EXCLUDED_PATHS,
    assert_runtime_routes,
    normalize_path,
)


def registered_routes(patterns, prefix=""):
    routes = set()
    for pattern in patterns:
        path = prefix + str(pattern.pattern)
        if isinstance(pattern, URLResolver):
            routes.update(registered_routes(pattern.url_patterns, path))
            continue
        normalized = normalize_path(path)
        if normalized in EXCLUDED_PATHS:
            continue
        # Django's DEBUG-only static() helper, not arbitrary business paths.
        callback = pattern.callback
        if getattr(callback, "__module__", "") == "django.views.static":
            continue
        view = getattr(callback, "cls", getattr(callback, "view_class", None))
        assert view is not None, f"Unclassified function route: {path}"
        if hasattr(callback, "actions"):
            methods = callback.actions
            assert all(hasattr(view, action) for action in methods.values()), path
        else:
            methods = [
                method for method in view.http_method_names if hasattr(view, method)
            ]
        routes.update((method.upper(), normalized) for method in methods)
    return routes


def test_all_actual_django_business_routes_are_registered():
    assert_runtime_routes("django", registered_routes(get_resolver().url_patterns))


def test_new_nested_urlconf_cannot_escape_inventory():
    class NewBusinessView(APIView):
        def get(self, request):
            return None

    patterns = [
        *get_resolver().url_patterns,
        path(
            "new-module/", include([path("new-business/", NewBusinessView.as_view())])
        ),
    ]
    with pytest.raises(AssertionError, match="/new-module/new-business"):
        assert_runtime_routes("django", registered_routes(patterns))
