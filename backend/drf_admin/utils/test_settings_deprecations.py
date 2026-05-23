from django.conf import settings


def test_removed_l10n_setting_is_not_defined():
    """Django 5 已移除 USE_L10N，项目不应继续定义该配置。"""
    assert not settings.is_overridden("USE_L10N")


def test_drf_yasg_compat_renderers_are_disabled():
    """drf_yasg 新版 renderer format 已变化，应关闭兼容 renderer 避免弃用警告。"""
    assert settings.SWAGGER_USE_COMPAT_RENDERERS is False


def test_default_password_must_be_explicit_and_not_weak():
    """新增用户默认密码必须显式来自环境配置，且不能继续使用 123456。"""
    assert settings.DEFAULT_PWD != "123456"
