# -*- coding: utf-8 -*-

import base64
import hashlib
import os

from Crypto.Cipher import AES
from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """基类模型"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 抽象模型类, 用于继承使用


class BasePasswordModels(models.Model):
    """需要密码加解密的基类模型"""

    LEGACY_PREFIX_START = 4
    LEGACY_PREFIX_END = 20
    GCM_PREFIX = "v2:"
    GCM_NONCE_SIZE = 16
    GCM_TAG_SIZE = 16

    class Meta:
        abstract = True

    @staticmethod
    def encrypt(row_password: str):
        """
        AES 加密登录密码
        :param row_password: 原明文密码
        :return: AES加密后密码
        """
        aes = AES.new(BasePasswordModels._gcm_key(), AES.MODE_GCM, nonce=os.urandom(BasePasswordModels.GCM_NONCE_SIZE))
        ciphertext, tag = aes.encrypt_and_digest(row_password.encode("utf-8"))
        payload = aes.nonce + tag + ciphertext
        return BasePasswordModels.GCM_PREFIX + base64.b64encode(payload).decode("utf-8")

    def set_password(self, field_name, field_value):
        """加密密码并保存实例"""
        self.__setattr__(field_name, self.encrypt(field_value))

    def get_password_display(self, field_name):
        """
        AES 解密登录密码
        :return: 原明文密码
        """
        password = str(self.__getattribute__(field_name))
        if password.startswith(BasePasswordModels.GCM_PREFIX):
            return BasePasswordModels._decrypt_gcm(password.removeprefix(BasePasswordModels.GCM_PREFIX))
        return BasePasswordModels._decrypt_legacy(password)

    @staticmethod
    def _gcm_key():
        """派生新密码加密密钥，避免直接截取 SECRET_KEY。"""
        return hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()

    @staticmethod
    def _legacy_key():
        """保留旧密文可读的兼容密钥。"""
        secret_key = settings.SECRET_KEY
        if len(secret_key) >= BasePasswordModels.LEGACY_PREFIX_END:
            return secret_key[BasePasswordModels.LEGACY_PREFIX_START:BasePasswordModels.LEGACY_PREFIX_END].encode(
                "utf-8"
            )
        return hashlib.sha256(secret_key.encode("utf-8")).digest()[:16]

    @staticmethod
    def _decrypt_legacy(password: str):
        """解密旧版 ECB 密文。"""
        aes = AES.new(BasePasswordModels._legacy_key(), AES.MODE_ECB)
        decrypted = aes.decrypt(base64.b64decode(password.encode("utf-8")))
        return decrypted.rstrip(b"\0").decode("utf-8")

    @staticmethod
    def _decrypt_gcm(payload: str):
        """解密新版 GCM 密文。"""
        raw = base64.b64decode(payload.encode("utf-8"))
        nonce = raw[:BasePasswordModels.GCM_NONCE_SIZE]
        tag = raw[
            BasePasswordModels.GCM_NONCE_SIZE : BasePasswordModels.GCM_NONCE_SIZE + BasePasswordModels.GCM_TAG_SIZE
        ]
        ciphertext = raw[BasePasswordModels.GCM_NONCE_SIZE + BasePasswordModels.GCM_TAG_SIZE :]
        aes = AES.new(BasePasswordModels._gcm_key(), AES.MODE_GCM, nonce=nonce)
        return aes.decrypt_and_verify(ciphertext, tag).decode("utf-8")
