# -*- coding: utf-8 -*-
"""
密码加解密相关测试
"""

import base64

from Crypto.Cipher import AES
from django.test import TestCase

from drf_admin.utils.models import BasePasswordModels


class PasswordBox(BasePasswordModels):
    """用于验证自定义密码加解密逻辑的测试模型。"""

    class Meta:
        app_label = "system"
        managed = False


class PasswordCryptoTestCase(TestCase):
    """验证密码加解密实现的关键行为"""

    def test_encrypt_and_decrypt_round_trip(self):
        """加密后再解密应恢复原文。"""

        password = "Newpass123!"
        box = PasswordBox()
        box.set_password("password", password)

        self.assertNotEqual(box.password, password)
        self.assertEqual(box.get_password_display("password"), password)

    def test_legacy_ecb_ciphertext_is_still_readable(self):
        """旧版 ECB 密文仍应可解密，避免历史密码失效。"""

        password = "Legacy123"
        raw = password.encode("utf-8")
        while len(raw) % 16 != 0:
            raw += b"\0"
        aes = AES.new(BasePasswordModels._legacy_key(), AES.MODE_ECB)
        box = PasswordBox()
        box.password = base64.b64encode(aes.encrypt(raw)).decode("utf-8")

        self.assertEqual(box.get_password_display("password"), password)
