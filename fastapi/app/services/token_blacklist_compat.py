"""
Token 黑名单服务兼容访问器。

这些属性只服务既有测试和过渡期调用，避免主服务类继续承载兼容样板。
"""

from datetime import datetime

from app.services.token_blacklist_memory import TokenBlacklistMemoryStore


class TokenBlacklistCompatibilityMixin:
    """提供内存存储的兼容属性访问。"""

    _memory_store: TokenBlacklistMemoryStore

    @property
    def _memory_blacklist(self) -> dict[str, datetime]:
        """兼容既有测试直接重置内存黑名单的入口。"""
        return self._memory_store.blacklist

    @_memory_blacklist.setter
    def _memory_blacklist(self, value: dict[str, datetime]) -> None:
        """兼容既有测试直接覆盖内存黑名单的入口。"""
        self._memory_store.blacklist = value

    @property
    def _memory_user_revocations(self) -> dict[int, datetime]:
        """兼容既有测试直接重置用户撤销标记的入口。"""
        return self._memory_store.user_revocations

    @_memory_user_revocations.setter
    def _memory_user_revocations(self, value: dict[int, datetime]) -> None:
        """兼容既有测试直接覆盖用户撤销标记的入口。"""
        self._memory_store.user_revocations = value
