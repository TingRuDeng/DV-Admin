"""本地登录令牌签发：密码登录、单点登录和刷新令牌共用同一份令牌结构。"""

from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.db.models.oauth import Users
from app.schemas.oauth import Token


def issue_login_tokens(user: Users, session_started_at: datetime | None = None) -> Token:
    """签发访问令牌和刷新令牌；刷新时传入原会话时间，保证用户级撤销仍然生效。"""
    started_at = session_started_at or datetime.now(timezone.utc)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims={
            "username": user.username,
            "name": user.name,
            "session_iat": started_at.timestamp(),
        },
    )
    refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        session_started_at=started_at,
    )
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
    )
