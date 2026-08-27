# -*- coding: utf-8 -*-

from rest_framework import serializers

from drf_admin.apps.system.models import Users


class ChangePasswordSerializer(serializers.Serializer):
    """
    个人中心修改密码序列化器
    """
    old_password = serializers.CharField(write_only=True, help_text="当前密码", required=False)
    new_password = serializers.CharField(
        write_only=True,
        help_text="新密码",
        required=False,
        max_length=20,
        min_length=6,
    )
    confirm_password = serializers.CharField(write_only=True, help_text="确认新密码", required=True)
    current_password = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(
        write_only=True,
        required=False,
        max_length=20,
        min_length=6,
    )

    def validate(self, attrs):
        old_password = attrs.get("old_password") or attrs.get("current_password")
        new_password = attrs.get("new_password") or attrs.get("password")
        if not old_password:
            raise serializers.ValidationError("原密码不能为空")
        if not new_password:
            raise serializers.ValidationError("新密码不能为空")
        if not self.instance.check_password(old_password):
            raise serializers.ValidationError('原密码错误')
        if attrs.get('confirm_password') != new_password:
            raise serializers.ValidationError('两次输入密码不一致')
        if len(new_password) < 6:
            raise serializers.ValidationError('密码长度不能少于6位')
        if not any(c.isdigit() for c in new_password):
            raise serializers.ValidationError('密码必须包含数字')
        if not any(c.isalpha() for c in new_password):
            raise serializers.ValidationError('密码必须包含字母')
        attrs["new_password"] = new_password
        return attrs

    def update(self, instance, validated_data):
        self.instance.set_password(validated_data["new_password"])
        self.instance.save()
        return self.instance

    def create(self, validated_data):
        raise NotImplementedError


class InformationSerializer(serializers.ModelSerializer):
    """
    个人中心获取个人信息序列化器
    """
    avatar = serializers.SerializerMethodField()
    dept_name = serializers.CharField(source="dept.name", read_only=True, default="")
    role_names = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'name',
            'mobile',
            'email',
            'avatar',
            'gender',
            'dept_name',
            'role_names',
            'create_time',
        ]

    def get_avatar(self, obj):
        if obj.image:
            return '/media/' + str(obj.image)
        else:
            return None

    def get_role_names(self, obj):
        return ",".join(obj.roles.values_list("name", flat=True))


class ChangeInformationSerializer(serializers.ModelSerializer):
    """
    个人中心修改个人信息序列化器
    """
    # mobile = serializers.RegexField(r'^1[3-9]\d{9}$', allow_blank=True, error_messages={'invalid': '手机号格式错误'})

    class Meta:
        model = Users
        fields = ['name', 'email', 'mobile', 'gender']

    @staticmethod
    def validate_mobile(mobile):
        """空手机号按未设置处理，避免唯一约束把多个空字符串视为重复值。"""
        return mobile or None


class ChangeAvatarSerializer(serializers.ModelSerializer):
    """
    个人中心修改个人头像序列化器
    """

    class Meta:
        model = Users
        fields = ['image']


class AvatarInfoSerializer(serializers.Serializer):
    """头像上传的双后端共享响应字段。"""

    avatar = serializers.CharField(read_only=True)
    url = serializers.CharField(read_only=True)
