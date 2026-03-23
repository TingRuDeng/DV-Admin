"""
验证码服务测试
测试 CaptchaService 的所有方法
"""
import pytest

from app.services.captcha_service import get_captcha_service


class TestCaptchaService:
    """测试验证码服务"""

    @pytest.mark.asyncio
    async def test_generate_captcha(self, db):
        """测试生成验证码"""
        service = get_captcha_service()
        key, base64_image = await service.create()

        assert key is not None
        assert base64_image is not None
        assert isinstance(key, str)
        assert isinstance(base64_image, str)
        assert len(key) > 0
        assert len(base64_image) > 0

    @pytest.mark.asyncio
    async def test_verify_captcha_wrong(self, db):
        """测试验证错误的验证码"""
        service = get_captcha_service()
        # 生成验证码
        key, _ = await service.create()

        # 验证错误的答案
        result = await service.verify(key, "wrong_answer")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_captcha_expired(self, db):
        """测试验证过期的验证码"""
        service = get_captcha_service()
        # 使用不存在的 key
        result = await service.verify("nonexistent_key", "any_answer")
        assert result is False

    @pytest.mark.asyncio
    async def test_generate_multiple_captchas(self, db):
        """测试生成多个验证码"""
        service = get_captcha_service()
        keys = set()
        for _ in range(5):
            key, _ = await service.create()
            keys.add(key)

        # 每个验证码的 key 应该是唯一的
        assert len(keys) == 5
