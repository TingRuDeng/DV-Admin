"""
Token 黑名单记录 helper 测试。
"""

from datetime import datetime, timedelta, timezone

from app.services.token_blacklist_records import (
    build_token_blacklist_record,
    build_user_revocation_record,
    is_token_revoked_by_time,
)


def test_build_token_blacklist_record():
    """应构造带 TTL、Key 和写入值的 Token 黑名单记录。"""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=90)

    record = build_token_blacklist_record(
        token="token",
        user_id=123,
        reason="logout",
        expires_at=expires_at,
        revoked_at=now,
    )

    assert record is not None
    assert record.ttl == 90
    assert record.key.startswith("token_blacklist:")
    assert record.expires_at == expires_at
    assert record.value == {
        "user_id": 123,
        "reason": "logout",
        "revoked_at": now.isoformat(),
    }


def test_build_token_blacklist_record_returns_none_for_expired_token():
    """已过期 Token 不需要进入黑名单。"""
    now = datetime.now(timezone.utc)
    expires_at = now - timedelta(seconds=1)

    record = build_token_blacklist_record(
        token="token",
        user_id=None,
        reason="logout",
        expires_at=expires_at,
        revoked_at=now,
    )

    assert record is None


def test_build_user_revocation_record():
    """应构造用户级撤销记录和刷新 Token 周期 TTL。"""
    now = datetime.now(timezone.utc)

    record = build_user_revocation_record(
        user_id=123,
        refresh_token_expire_days=7,
        revoked_at=now,
    )

    assert record.key == "token_blacklist:user:123"
    assert record.ttl == 7 * 24 * 60 * 60
    assert record.revoked_at == now


def test_is_token_revoked_by_time():
    """签发时间早于撤销时间时，Token 应视为已撤销。"""
    now = datetime.now(timezone.utc)
    revoked_at = now - timedelta(minutes=5)

    assert is_token_revoked_by_time(now - timedelta(minutes=10), revoked_at.isoformat()) is True
    assert is_token_revoked_by_time(now, revoked_at.isoformat()) is False
