# -*- coding: utf-8 -*-

from rest_framework import serializers

from drf_admin.apps.system.models import Users


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    个人中心修改密码序列化器
    """
    current_password = serializers.CharField(write_only=True, help_text="当前密码", required=True)
    confirm_password = serializers.CharField(write_only=True, help_text="确认新密码", required=True)

    class Meta:
        model = Users
        fields = ['current_password', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {
                'required': True,
                'max_length': 20,
                'min_length': 6,
                'write_only': True,
                'error_messages': {
                    'max_length': '密码长度应在6 到 20位',
                    'min_length': '密码长度应在6 到 20位',
                }
            }
        }

    def validate(self, attrs):
        if not self.instance.check_password(attrs.get('current_password')):
            raise serializers.ValidationError('原密码错误')
        if attrs.get('confirm_password') != attrs.get('password'):
            raise serializers.ValidationError('两次输入密码不一致')
        return attrs

    def update(self, instance, validated_data):
        self.instance.set_password(validated_data.get('password'))
        self.instance.save()
        return self.instance


class InformationSerializer(serializers.ModelSerializer):
    """
    个人中心获取个人信息序列化器
    """
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ['id', 'username', 'name', 'mobile', 'email', 'avatar']

    def get_avatar(self, obj):
        if obj.image:
            return '/media/' + str(obj.image)
        else:
            return None


class ChangeInformationSerializer(serializers.ModelSerializer):
    """
    个人中心修改个人信息序列化器
    """
    # mobile = serializers.RegexField(r'^1[3-9]\d{9}$', allow_blank=True, error_messages={'invalid': '手机号格式错误'})

    class Meta:
        model = Users
        fields = ['name']

    # @staticmethod
    # def validate_mobile(mobile):
    #     # 避免字段为 '' 时 models unique约束失败
    #     if mobile == '':
    #         return None
    #     else:
    #         return mobile


class ChangeAvatarSerializer(serializers.ModelSerializer):
    """
    个人中心修改个人头像序列化器
    """

    class Meta:
        model = Users
        fields = ['image']
