"""
Token 黑名单测试共享夹具。
"""
import pytest

from app.services.token_blacklist import token_blacklist_service


@pytest.fixture(autouse=True)
def reset_token_blacklist_service():
    """每个测试前后重置全局黑名单服务状态。"""
    token_blacklist_service._redis = None
    token_blacklist_service._memory_blacklist = {}
    token_blacklist_service._memory_user_revocations = {}
    yield
    token_blacklist_service._redis = None
    token_blacklist_service._memory_blacklist = {}
    token_blacklist_service._memory_user_revocations = {}
