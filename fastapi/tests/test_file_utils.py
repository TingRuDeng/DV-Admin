"""
文件工具测试
测试 file 模块的功能
"""
import os
import tempfile
from io import BytesIO

import pytest
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.utils.file import (
    allowed_file,
    format_file_size,
    get_file_size,
    save_upload_file,
    secure_filename,
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

    def test_allowed_file_rejects_svg(self):
        """通用上传禁止 SVG，避免同源静态托管执行脚本。"""
        assert allowed_file("payload.svg") is False

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

    @pytest.mark.asyncio
    async def test_save_upload_file_streams_to_atomic_target(self, tmp_path, monkeypatch):
        """上传内容分块写入临时文件，成功后再原子替换为目标文件。"""
        monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
        upload = UploadFile(filename="report.txt", file=BytesIO(b"streamed content"))

        relative_path = await save_upload_file(
            upload,
            subdir="files/7",
            max_size=1024,
        )

        saved_path = tmp_path / relative_path
        assert saved_path.read_bytes() == b"streamed content"
        assert not list(tmp_path.rglob("*.part"))

    @pytest.mark.asyncio
    async def test_save_upload_file_cleans_partial_file_on_size_error(
        self,
        tmp_path,
        monkeypatch,
    ):
        """超过上限时不留下可见目标或分块临时文件。"""
        monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
        upload = UploadFile(filename="large.txt", file=BytesIO(b"too large"))

        with pytest.raises(ValidationError):
            await save_upload_file(upload, subdir="files/7", max_size=4)

        assert not any(path.is_file() for path in tmp_path.rglob("*"))

    @pytest.mark.asyncio
    async def test_save_upload_file_accepts_exact_size_limit(self, tmp_path, monkeypatch):
        """文件大小等于上限时允许保存，锁定边界没有少算一个字节。"""
        monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
        upload = UploadFile(filename="exact.txt", file=BytesIO(b"1234"))

        relative_path = await save_upload_file(upload, max_size=4)

        assert (tmp_path / relative_path).read_bytes() == b"1234"
