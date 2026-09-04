# -*- coding: utf-8 -*-

import logging

from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_admin.apps.information.serializers.centre import (
    AvatarInfoSerializer,
    ChangeAvatarSerializer,
    ChangeInformationSerializer,
    ChangePasswordSerializer,
    InformationSerializer,
)
from drf_admin.utils.audit import set_audit_object

logger = logging.getLogger(__name__)


class _CurrentUserAuditMixin:
    """为个人中心写入口登记当前用户对象。"""

    def initial(self, request, *args, **kwargs):
        user = getattr(request, "user", None)
        set_audit_object(request, "system.users", getattr(user, "pk", ""))
        return super().initial(request, *args, **kwargs)

    def set_current_user_audit(self, request):
        user = getattr(request, "user", None)
        try:
            fields = list(request.data.keys())
        except Exception:  # noqa: BLE001 - 解析错误由 DRF 返回
            fields = []
        set_audit_object(
            request,
            "system.users",
            getattr(user, "pk", ""),
            changed_fields=fields,
        )


class CentreAPIView(_CurrentUserAuditMixin, GenericAPIView):
    """
    get:
    个人中心--获取个人信息

    个人中心获取个人信息, status: 200(成功), return: 当前登录用户的个人信息
    """

    serializer_class = InformationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = InformationSerializer(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        self.set_current_user_audit(request)
        serializer = ChangeInformationSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(InformationSerializer(request.user).data)


class ChangePasswordAPIView(_CurrentUserAuditMixin, mixins.UpdateModelMixin, GenericAPIView):
    """
    put:
    个人中心--修改密码

    个人中心修改密码, status: 200(成功), return: None
    """

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        self.set_current_user_audit(request)
        return self.update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class ChangeInformationAPIView(_CurrentUserAuditMixin, mixins.UpdateModelMixin, GenericAPIView):
    """
    put:
    个人中心--修改个人信息

    个人中心修改个人信息, status: 200(成功), return: 修改后的个人信息
    """

    serializer_class = ChangeInformationSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        self.set_current_user_audit(request)
        return self.update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class ChangeAvatarAPIView(_CurrentUserAuditMixin, GenericAPIView):
    """
    post:
    上传用户头像

    上传用户头像图片，将保存在media/avatar/目录下，status: 200(成功), return: 头像URL和上传成功信息
    """

    serializer_class = ChangeAvatarSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        self.set_current_user_audit(request)
        # 获取当前登录用户
        user = request.user

        # 检查请求中是否包含图片文件
        upload = request.data.get("file") or request.data.get("image")
        if upload is None:
            return Response(
                {"detail": "请求中未包含图片文件", "error_code": "NO_IMAGE_PROVIDED"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查image字段是否为文件对象
        if isinstance(upload, str):
            # 如果是字符串，可能是前端传递了base64或者有其他问题
            return Response(
                {
                    "detail": "上传的图片数据格式不正确，请确保使用正确的multipart/form-data格式",
                    "error_code": "INVALID_IMAGE_FORMAT",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 验证并保存图片
            serializer = self.get_serializer(instance=user, data={"image": upload})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            avatar_url = request.build_absolute_uri(user.image.url)

            response_serializer = AvatarInfoSerializer(
                {"avatar": user.image.name, "url": avatar_url}
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except ValidationError:
            # DRF 的校验错误需要让上层正常处理
            raise
        except Exception:
            logger.exception("头像上传失败")
            return Response(
                {"detail": "头像上传失败，请稍后重试", "error_code": "UPLOAD_FAILED"},
                status=status.HTTP_400_BAD_REQUEST,
            )
