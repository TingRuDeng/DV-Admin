# -*- coding: utf-8 -*-
"""
安全验证器模块

提供生产环境安全配置验证功能。
"""

import os
import re
import secrets
import warnings
from typing import List, Optional


class SecurityValidationError(Exception):
    """安全验证错误"""
    pass


class SecurityValidator:
    """安全配置验证器"""

    # 弱密码列表
    WEAK_PASSWORDS = {
        "123456",
        "password",
        "admin",
        "admin123",
        "root",
        "root123",
        "test",
        "test123",
        "qwerty",
        "abc123",
        "111111",
        "000000",
        "password123",
        "admin@123",
        "Admin123",
        "Admin@123",
    }

    # 最小密钥长度
    MIN_SECRET_KEY_LENGTH = 32

    # 推荐密钥长度
    RECOMMENDED_SECRET_KEY_LENGTH = 64

    @classmethod
    def validate_secret_key(cls, secret_key: Optional[str], is_production: bool) -> List[str]:
        """
        验证 SECRET_KEY 安全性

        Args:
            secret_key: 密钥值
            is_production: 是否为生产环境

        Returns:
            警告消息列表
        """
        warnings_list = []

        # 生产环境必须设置 SECRET_KEY
        if is_production and not secret_key:
            raise SecurityValidationError(
                "生产环境必须设置 SECRET_KEY 环境变量！"
                "请生成一个安全的密钥并设置到环境变量中。"
            )

        # 检查密钥是否存在
        if not secret_key:
            warnings_list.append(
                "WARNING: SECRET_KEY 未设置，将使用临时生成的密钥。"
                "这会导致应用重启后所有 JWT token 失效。"
            )
            return warnings_list

        # 检查密钥长度
        if len(secret_key) < cls.MIN_SECRET_KEY_LENGTH:
            if is_production:
                raise SecurityValidationError(
                    f"生产环境 SECRET_KEY 长度必须至少 {cls.MIN_SECRET_KEY_LENGTH} 字符！"
                    f"当前长度: {len(secret_key)} 字符。"
                )
            else:
                warnings_list.append(
                    f"WARNING: SECRET_KEY 长度过短（{len(secret_key)} 字符），"
                    f"建议至少 {cls.MIN_SECRET_KEY_LENGTH} 字符。"
                )

        # 检查密钥强度
        if len(secret_key) < cls.RECOMMENDED_SECRET_KEY_LENGTH:
            warnings_list.append(
                f"WARNING: SECRET_KEY 长度 {len(secret_key)} 字符，"
                f"推荐使用 {cls.RECOMMENDED_SECRET_KEY_LENGTH} 字符以上的密钥。"
            )

        # 检查密钥是否为常见弱密钥
        weak_key_patterns = [
            r"^your-secret-key$",
            r"^secret$",
            r"^key$",
            r"^changeme$",
            r"^test",
            r"^dev",
            r"^development",
            r"^{+$",
            r"^\[+$",
        ]

        for pattern in weak_key_patterns:
            if re.match(pattern, secret_key, re.IGNORECASE):
                if is_production:
                    raise SecurityValidationError(
                        f"生产环境 SECRET_KEY 不能使用默认或弱密钥！"
                        f"请使用安全的随机密钥。"
                    )
                else:
                    warnings_list.append(
                        "WARNING: SECRET_KEY 使用了默认或弱密钥模式，"
                        "生产环境请务必更换为安全的随机密钥。"
                    )
                break

        # 检查密钥熵值（简单检查字符多样性）
        unique_chars = len(set(secret_key))
        if unique_chars < 8:
            if is_production:
                raise SecurityValidationError(
                    f"生产环境 SECRET_KEY 字符多样性不足！"
                    f"仅包含 {unique_chars} 种不同字符，建议使用更复杂的密钥。"
                )
            else:
                warnings_list.append(
                    f"WARNING: SECRET_KEY 字符多样性较低（{unique_chars} 种字符），"
                    f"建议使用包含多种字符的复杂密钥。"
                )

        return warnings_list

    @classmethod
    def validate_password_strength(cls, password: str) -> List[str]:
        """
        验证密码强度

        Args:
            password: 密码

        Returns:
            警告消息列表
        """
        warnings_list = []

        # 检查是否为弱密码
        if password.lower() in cls.WEAK_PASSWORDS:
            warnings_list.append(
                f"WARNING: 默认密码 '{password}' 是常见弱密码，"
                "生产环境请务必修改为强密码！"
            )

        # 检查密码长度
        if len(password) < 8:
            warnings_list.append(
                f"WARNING: 默认密码长度过短（{len(password)} 字符），"
                "建议至少 8 字符。"
            )

        # 检查密码复杂度
        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

        complexity_score = sum([has_lower, has_upper, has_digit, has_special])

        if complexity_score < 2:
            warnings_list.append(
                "WARNING: 默认密码复杂度过低，"
                "建议包含大小写字母、数字和特殊字符。"
            )

        return warnings_list

    @classmethod
    def validate_production_settings(
        cls,
        app_env: str,
        debug: bool,
        secret_key: Optional[str],
        default_password: str,
    ) -> List[str]:
        """
        验证生产环境设置

        Args:
            app_env: 应用环境
            debug: 调试模式
            secret_key: 密钥
            default_password: 默认密码

        Returns:
            警告消息列表
        """
        warnings_list = []
        is_production = app_env.lower() == "production"

        # 生产环境检查
        if is_production:
            # 检查调试模式
            if debug:
                warnings_list.append(
                    "WARNING: 生产环境不应启用 DEBUG 模式！"
                    "请设置 DEBUG=false。"
                )

            # 验证密钥
            key_warnings = cls.validate_secret_key(secret_key, is_production)
            warnings_list.extend(key_warnings)

            # 验证默认密码
            password_warnings = cls.validate_password_strength(default_password)
            warnings_list.extend(password_warnings)

        else:
            # 开发环境警告
            dev_warnings = cls.validate_secret_key(secret_key, is_production)
            warnings_list.extend(dev_warnings)

            password_warnings = cls.validate_password_strength(default_password)
            warnings_list.extend(password_warnings)

        return warnings_list

    @classmethod
    def generate_secure_key(cls, length: int = 64) -> str:
        """
        生成安全的随机密钥

        Args:
            length: 密钥长度

        Returns:
            安全的随机密钥字符串
        """
        return secrets.token_urlsafe(length)

    @classmethod
    def print_security_warnings(cls, warnings_list: List[str]) -> None:
        """
        打印安全警告

        Args:
            warnings_list: 警告消息列表
        """
        for warning_msg in warnings_list:
            warnings.warn(warning_msg, UserWarning, stacklevel=3)
