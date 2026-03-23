"""
核心安全模块测试
测试 security 模块的功能
"""

from app.core.security import get_password_hash, verify_password


class TestSecurity:
    """测试安全模块"""

    def test_password_hash(self):
        """测试密码哈希"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """测试验证正确的密码"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_wrong(self):
        """测试验证错误的密码"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password("wrong_password", hashed) is False

    def test_different_passwords_different_hashes(self):
        """测试不同密码生成不同的哈希"""
        password1 = "password1"
        password2 = "password2"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2

    def test_same_password_different_hashes(self):
        """测试相同密码生成不同的哈希（因为有盐值）"""
        password = "same_password"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # 由于 bcrypt 使用随机盐值，相同密码的哈希应该不同
        assert hash1 != hash2

    def test_empty_password(self):
        """测试空密码"""
        password = ""
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_long_password(self):
        """测试长密码"""
        password = "a" * 100
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
