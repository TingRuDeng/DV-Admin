# -*- coding: utf-8 -*-

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from drf_admin.apps.information.serializers.centre import (
    ChangePasswordSerializer, ChangeInformationSerializer, ChangeAvatarSerializer
)


class ChangePasswordAPIView(mixins.UpdateModelMixin, GenericAPIView):
    """
    put:
    个人中心--修改密码

    个人中心修改密码, status: 200(成功), return: None
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class ChangeInformationAPIView(mixins.UpdateModelMixin, GenericAPIView):
    """
    put:
    个人中心--修改个人信息

    个人中心修改个人信息, status: 200(成功), return: 修改后的个人信息
    """
    serializer_class = ChangeInformationSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class ChangeAvatarAPIView(GenericAPIView):
    """
    post:
    上传用户头像

    上传用户头像图片，将保存在media/avatar/目录下，status: 200(成功), return: 头像URL和上传成功信息
    """
    serializer_class = ChangeAvatarSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # 获取当前登录用户
        user = request.user

        # 检查请求中是否包含图片文件
        if 'image' not in request.data:
            return Response(
                {'detail': '请求中未包含图片文件', 'error_code': 'NO_IMAGE_PROVIDED'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查image字段是否为文件对象
        image_data = request.data.get('image')
        if isinstance(image_data, str):
            # 如果是字符串，可能是前端传递了base64或者有其他问题
            return Response(
                {'detail': '上传的图片数据格式不正确，请确保使用正确的multipart/form-data格式',
                 'error_code': 'INVALID_IMAGE_FORMAT'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 验证并保存图片
            serializer = self.get_serializer(instance=user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # 构建完整的头像URL
            avatar_url = request.build_absolute_uri(serializer.data['image'])

            return Response({
                'detail': '头像更新成功',
                'url': avatar_url,
                'image': serializer.data['image']
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # 捕获并返回详细的错误信息
            return Response(
                {'detail': f'头像上传失败: {str(e)}', 'error_code': 'UPLOAD_FAILED'},
                status=status.HTTP_400_BAD_REQUEST
            )