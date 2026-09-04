
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from drf_admin.utils.audit import set_audit_context, set_audit_object
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
    # 模型名与对外业务对象名并不总是一一对应（Permissions 对外称 menus）。
    AUDIT_OBJECT_TYPES = {
        "users": "system.users",
        "roles": "system.roles",
        "permissions": "system.menus",
        "departments": "system.departments",
        "dicts": "system.dicts",
        "dictitems": "system.dict_items",
        "notices": "system.notices",
    }

    def get_audit_object_type(self) -> str:
        """返回稳定的业务对象类型，供两套后端共享审计筛选语义。"""
        explicit = getattr(self, "audit_object_type", "")
        if explicit:
            return explicit
        model = self.get_model()
        model_name = getattr(getattr(model, "_meta", None), "model_name", "")
        return self.AUDIT_OBJECT_TYPES.get(
            model_name,
            f"system.{model_name}" if model_name else "system.unknown",
        )

    def _audit_object_id(self) -> str:
        lookup = self.lookup_url_kwarg or self.lookup_field
        value = self.kwargs.get(lookup)
        return "" if value is None else str(value)

    def _set_audit_request(self, object_id: object = None) -> None:
        """在校验前登记对象类型，确保失败请求也能按对象检索。"""
        if object_id is None:
            object_id = self._audit_object_id()
        changed_fields = []
        try:
            data = self.request.data
            if hasattr(data, "keys"):
                changed_fields = [str(field) for field in data.keys()]
        except Exception:  # noqa: BLE001 - 请求体解析失败由 DRF 自己返回错误
            changed_fields = []
        set_audit_object(
            self.request,
            self.get_audit_object_type(),
            object_id,
            changed_fields=changed_fields,
        )

        # 批量接口只保存有界 ID 摘要，避免把任意长度列表写入单条日志。
        if self.action in {"multiple_delete", "delete_by_ids", "retry_batch_delete"}:
            raw_ids = []
            if isinstance(getattr(self.request, "data", None), dict):
                raw_ids = self.request.data.get("ids", [])
            if isinstance(raw_ids, str):
                raw_ids = [item.strip() for item in raw_ids.split(",") if item.strip()]
            if not isinstance(raw_ids, (list, tuple)):
                raw_ids = []
            set_audit_context(
                self.request,
                batch_count=len(raw_ids),
                batch_ids=[str(item)[:255] for item in list(raw_ids)[:100]],
            )

    def initial(self, request, *args, **kwargs):
        self._set_audit_request()
        return super().initial(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        object_id = response.data.get("id") if isinstance(getattr(response, "data", None), dict) else ""
        if object_id not in (None, ""):
            self._set_audit_request(object_id)
        return response

    def update(self, request, *args, **kwargs):
        self._set_audit_request(self._audit_object_id())
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._set_audit_request(self._audit_object_id())
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._set_audit_request(self._audit_object_id())
        return super().destroy(request, *args, **kwargs)

    def multiple_delete(self, request, *args, **kwargs):
        self._set_audit_request()
        return super().multiple_delete(request, *args, **kwargs)


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
                parent_key = 'parent_id' if 'parent_id' in tree_dict[i] else 'parent'
                if tree_dict[i].get(parent_key):
                    parent = tree_dict[i][parent_key]
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
