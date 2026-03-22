# -*- coding: utf-8 -*-
"""
文件工具测试
测试 file 模块的功能
"""
import pytest
import os
import tempfile

from app.utils.file import (
    allowed_file,
    secure_filename,
    get_file_size,
    format_file_size,
)


class TestFileUtils:
    """测试文件工具"""

    def test_allowed_file(self):
        """测试检查允许的文件"""
        assert allowed_file("test.jpg") is True
        assert allowed_file("test.png") is True
        assert allowed_file("test.pdf") is True
        assert allowed_file("test.xyz") is False
        assert allowed_file("no_extension") is False

    def test_secure_filename(self):
        """测试安全文件名"""
        assert secure_filename("test.txt") == "test.txt"
        # 路径部分被移除，危险字符被替换
        result = secure_filename("../../../etc/passwd")
        assert "passwd" in result
        assert "test" in secure_filename("test file.txt")

    def test_format_file_size(self):
        """测试格式化文件大小"""
        assert format_file_size(0) == "0.0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_get_file_size(self):
        """测试获取文件大小"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        
        try:
            size = get_file_size(temp_path)
            assert size == 12
        finally:
            os.unlink(temp_path)

    def test_get_file_size_nonexistent(self):
        """测试获取不存在文件的大小"""
        size = get_file_size("/nonexistent/file/path")
        assert size == 0
