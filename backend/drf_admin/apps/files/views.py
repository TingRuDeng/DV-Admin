from __future__ import annotations

from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_admin.apps.files.storage import (
    allowed_file,
    ensure_file_owner,
    normalize_file_path,
    resolve_upload_path,
    save_upload_file,
)


class FileAPIView(APIView):
    """通用文件上传和所有者删除接口。"""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload = request.FILES.get("file")
        if upload is None or not upload.name:
            raise ValidationError("文件名不能为空")
        if not allowed_file(upload.name):
            raise ValidationError("不支持的文件类型")

        relative_path = save_upload_file(upload, request.user.id)
        file_url = request.build_absolute_uri(f"{settings.MEDIA_URL}{relative_path}")
        return Response(
            {
                "name": upload.name,
                "url": file_url,
                "path": relative_path,
            }
        )

    def delete(self, request):
        file_path = request.query_params.get("filePath") or request.query_params.get("file_path", "")
        normalized_path = normalize_file_path(file_path)
        ensure_file_owner(normalized_path, request.user.id)
        full_path = resolve_upload_path(normalized_path)
        if not full_path.exists() or not full_path.is_file():
            raise ValidationError("文件不存在")
        full_path.unlink()
        return Response(data={})
