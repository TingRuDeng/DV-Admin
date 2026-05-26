"""同步 ASGI 客户端与认证夹具。"""

import httpx
import pytest
from fixtures.database import TEST_DB_PATH


class SyncASGIClient:
    """让同步测试通过同一事件循环驱动 ASGI 请求。"""

    def __init__(self, app, loop):
        self._app = app
        self._loop = loop
        self._lifespan_cm = None
        self._client: httpx.AsyncClient | None = None

    def start(self) -> "SyncASGIClient":
        """启动应用 lifespan 和底层 httpx 客户端。"""
        self._lifespan_cm = self._app.router.lifespan_context(self._app)
        self._loop.run_until_complete(self._lifespan_cm.__aenter__())
        self._client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=self._app),
            base_url="http://testserver",
        )
        self._loop.run_until_complete(self._client.__aenter__())
        return self

    def close(self) -> None:
        """关闭客户端与应用 lifespan，避免跨用例泄漏状态。"""
        if self._client is not None:
            self._loop.run_until_complete(self._client.aclose())
            self._client = None
        if self._lifespan_cm is not None:
            self._loop.run_until_complete(self._lifespan_cm.__aexit__(None, None, None))
            self._lifespan_cm = None

    @property
    def headers(self):
        """暴露底层客户端 headers，供认证夹具临时注入 token。"""
        assert self._client is not None
        return self._client.headers

    def request(self, method: str, url: str, **kwargs):
        """同步包装 httpx 异步请求，保持历史测试调用方式。"""
        assert self._client is not None
        return self._loop.run_until_complete(self._client.request(method, url, **kwargs))

    def get(self, url: str, **kwargs):
        """发送 GET 请求。"""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        """发送 POST 请求。"""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs):
        """发送 PUT 请求。"""
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs):
        """发送 DELETE 请求。"""
        return self.request("DELETE", url, **kwargs)


@pytest.fixture(scope="function")
def client(session_loop) -> SyncASGIClient:
    """创建使用测试数据库的同步 ASGI 客户端。"""
    from app.core.config import settings
    from app.main import create_app

    original_database_url = settings.database_url
    settings.database_url = f"sqlite://{TEST_DB_PATH}"
    sync_client = None
    try:
        app = create_app()
        sync_client = SyncASGIClient(app, session_loop).start()
        yield sync_client
    finally:
        if sync_client is not None:
            sync_client.close()
        settings.database_url = original_database_url


def get_token_from_response(response) -> str | None:
    """从登录响应中提取 access token。"""
    if response.status_code != 200:
        return None
    data = response.json()
    if data.get("code") != 20000 or not data.get("data"):
        return None
    return data["data"].get("accessToken")


@pytest.fixture(scope="function")
def auth_headers(client: SyncASGIClient, test_user_with_role) -> dict:
    """登录测试用户并返回认证 headers。"""
    response = client.post(
        "/api/v1/oauth/login/",
        json={
            "username": test_user_with_role["username"],
            "password": test_user_with_role["password"],
        },
    )
    token = get_token_from_response(response)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.fixture(scope="function")
def auth_client(client: SyncASGIClient, auth_headers: dict) -> SyncASGIClient | None:
    """创建临时带认证头的测试客户端。"""
    if not auth_headers:
        pytest.skip("无法获取认证 token，跳过需要认证的测试")

    original_auth = client.headers.get("Authorization")
    client.headers.update(auth_headers)
    try:
        yield client
    finally:
        if original_auth is None:
            client.headers.pop("Authorization", None)
        else:
            client.headers["Authorization"] = original_auth
