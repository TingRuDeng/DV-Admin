
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError

from drf_admin.utils.permissions import RBACPermission
from drf_admin.utils.swagger_schema import OperationIDAutoSchema


class MultipleDestroyMixin:
    """
    自定义批量删除mixin
    """
    swagger_schema = OperationIDAutoSchema

    class MultipleDeleteSerializer(serializers.Serializer):
        ids = serializers.ListField(required=True, write_only=True)

    def validate_ids(self, delete_ids):
        # 验证object传入的删除id列表
        if not delete_ids:
            raise ValidationError('参数错误,ids为必传参数')
        if not isinstance(delete_ids, list):
            raise ValidationError('ids格式错误,必须为List')
        queryset = self.get_queryset()
        del_queryset = queryset.filter(id__in=delete_ids)
        if len(delete_ids) != del_queryset.count():
            raise ValidationError('删除数据不存在')
        return del_queryset

    @swagger_auto_schema(request_body=MultipleDeleteSerializer)
    def multiple_delete(self, request, *args, **kwargs):
        delete_ids = request.data.get('ids')
        del_queryset = self.validate_ids(delete_ids)
        del_queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AutoPermissionModelViewSet(ModelViewSet):
    """
    默认添加权限标识的ModelViewSet基类
    权限格式：app.model.action
    （自动生成权限标识+支持自定义）
    """
    permission_classes = [RBACPermission]
    queryset = None  # 需在子类中指定
    serializer_class = None  # 需在子类中指定

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_permissions = self._generate_required_permissions()

    def _generate_required_permissions(self):
        """根据model自动生成权限"""
        model = self.get_model()
        if not model:
            return {}

        # 权限标识格式：app.model.action
        app_label = _get_model_app_label(model)
        model_name = _get_model_name(model)  # 模型小写名称

        # Action与权限动作的映射
        action_mapping = self.get_action_permission_mapping()

        required_permissions = {}
        for action, action_suffix in action_mapping.items():
            permission_code = f"{app_label}:{model_name}:{action_suffix}"
            required_permissions[action] = [permission_code]
        return required_permissions

    def get_model(self):
        """获取关联的模型"""
        if hasattr(self, 'model'):
            return self.model
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.model
        if hasattr(self, 'serializer_class') and hasattr(self.serializer_class, 'Meta') and hasattr(self.serializer_class.Meta, 'model'):
            return self.serializer_class.Meta.model
        return None

    @staticmethod
    def get_action_permission_mapping():
        """Action与权限动作的映射关系"""
        return {
            'list': 'query',
            'retrieve': 'query',
            'create': 'add',
            'update': 'edit',
            'partial_update': 'edit',
            'destroy': 'delete',
            'multiple_delete': 'delete',
        }


class AutoPermissionAPIView(APIView):
    """
    自动生成权限的APIView基类
    权限格式：app.model.action
    """
    permission_classes = [RBACPermission]
    # # 需在子类中指定或通过queryset指定
    # model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_permissions = self._generate_required_permissions()

    def _generate_required_permissions(self):
        """根据model和HTTP方法自动生成权限"""
        model = self.get_model()
        if not model:
            return {}

        # 权限格式：app.model.action
        app_label = _get_model_app_label(model)
        model_name = _get_model_name(model)

        # HTTP方法与权限动作的映射
        method_mapping = self.get_method_permission_mapping()

        required_permissions = {}
        for method, action_suffix in method_mapping.items():
            permission_code = f"{app_label}:{model_name}:{action_suffix}"
            required_permissions[method] = [permission_code]

        return required_permissions

    def get_model(self):
        """获取关联的模型"""
        # 优先从显式设置的model属性获取
        if hasattr(self, 'model') and self.model is not None:
            return self.model
        # 其次从queryset获取
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.model

    @staticmethod
    def get_method_permission_mapping():
        """HTTP方法与权限动作的映射关系（可重写）"""
        return {
            'get': 'query',
            'post': 'add',
            'put': 'edit',
            'patch': 'edit',
            'delete': 'delete',
        }


class AdminViewSet(AutoPermissionModelViewSet, MultipleDestroyMixin):
    """
    继承AutoPermissionModelViewSet, 并新增MultipleDestroyMixin
    添加multiple_delete action
    """
    pass


# 辅助方法用于安全访问model的meta属性
def _get_model_app_label(model):
    """安全地获取模型的应用标签"""
    if hasattr(model, '_meta') and hasattr(model._meta, 'app_label'):
        return model._meta.app_label
    return ''


def _get_model_name(model):
    """安全地获取模型的名称"""
    if hasattr(model, '_meta') and hasattr(model._meta, 'model_name'):
        return model._meta.model_name
    # 如果没有_meta属性，尝试从类名获取
    return model.__name__.lower()


class OptionsSerializer(serializers.ModelSerializer):
    """
    Options类型View使用的基类序列化器
    """
    id = serializers.IntegerField()
    label = serializers.CharField(max_length=20, source='name')


class TreeSerializer(serializers.ModelSerializer):
    """
    TreeAPIView使用的基类序列化器
    """
    id = serializers.IntegerField()
    label = serializers.CharField(max_length=20, source='name')
    parent = serializers.PrimaryKeyRelatedField(read_only=True)


class TreeAPIView(ListAPIView):
    """
    定义Element Tree树结构
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        tree_dict = {}
        tree_data = []
        try:
            for item in serializer.data:
                tree_dict[item['id']] = item
            for i in tree_dict:
                if tree_dict[i]['parent']:
                    parent = tree_dict[i]['parent']
                    parent = tree_dict[parent]
                    parent.setdefault('children', []).append(tree_dict[i])
                else:
                    tree_data.append(tree_dict[i])
            results = tree_data
        except KeyError:
            results = serializer.data
        # if page is not None:
        #     return self.get_paginated_response(results)
        return Response(results)


class ChoiceAPIView(APIView):
    """
    model choice字段API, 需指定choice属性或覆盖get_choice方法
    """
    choice = None

    def get(self, request):
        methods = [{'value': value[0], 'label': value[1]} for value in self.get_choice()]
        return Response(data={'results': methods})

    def get_choice(self):
        assert self.choice is not None, (
                "'%s' 应该包含一个`choice`属性,或覆盖`get_choice()`方法."
                % self.__class__.__name__
        )
        assert isinstance(self.choice, tuple) and len(self.choice) > 0, 'choice数据错误, 应为二维元组'
        for values in self.choice:
            assert isinstance(values, tuple) and len(values) == 2, 'choice数据错误, 应为二维元组'
        return self.choice