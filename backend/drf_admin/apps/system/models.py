
import os
import json
import uuid

from django.db import models
from django.utils import timezone
from drf_admin.utils.models import BaseModel
from django.contrib.auth.models import AbstractUser


# 自定义头像上传路径函数，生成随机文件名
def user_avatar_path(instance, filename):
    # 获取当前日期，格式：年/月
    date_path = timezone.now().strftime('%Y/%m')
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 生成随机文件名
    random_name = f"{uuid.uuid4().hex}.{ext}"
    # 返回完整的上传路径
    return os.path.join('avatar', date_path, random_name)


# class Permissions(BaseModel):
#     """
#     权限
#     """
#     method_choices = (
#         (u'POST', u'增'),
#         (u'DELETE', u'删'),
#         (u'PUT', u'改'),
#         (u'PATCH', u'局部改'),
#         (u'GET', u'查')
#     )
#
#     name = models.CharField(max_length=30, verbose_name='权限名')
#     sign = models.CharField(max_length=30, unique=True, verbose_name='权限标识')
#     menu = models.BooleanField(verbose_name='是否为菜单')  # True为菜单,False为接口
#     method = models.CharField(max_length=8, blank=True, default='', choices=method_choices, verbose_name='方法')
#     path = models.CharField(max_length=200, blank=True, default='', verbose_name='请求路径正则')
#     pid = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父权限')
#     desc = models.CharField(max_length=30, blank=True, default='', verbose_name='权限描述')
#
#     objects = models.Manager()
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         db_table = 'system_permissions'
#         verbose_name = '权限'
#         verbose_name_plural = verbose_name
#         ordering = ['id']


class Permissions(BaseModel):
    """
    菜单
    """
    # method_choices = (
    #     (u'POST', u'增'),
    #     (u'DELETE', u'删'),
    #     (u'PUT', u'改'),
    #     (u'PATCH', u'局部改'),
    #     (u'GET', u'查')
    # )

    type_choices = (
        ('CATALOG', '根目录'),
        ('MENU', '菜单'),
        ('BUTTON', '按钮'),
        ('EXTLINK', '外链')
    )

    name = models.CharField(max_length=30, verbose_name='名称')
    type = models.CharField(max_length=8, blank=True, default='', choices=type_choices, verbose_name='权限类型')
    route_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='路由名')
    route_path = models.CharField(max_length=200, blank=True, null=True, verbose_name='路由路径')
    component = models.CharField(max_length=200, blank=True, null=True, verbose_name='组件路径')
    sort = models.IntegerField(default=0, verbose_name='排序')
    visible = models.IntegerField(default=1, verbose_name='是否可见')
    icon = models.CharField(max_length=30, blank=True, null=True, verbose_name='图标')
    redirect = models.CharField(max_length=200, blank=True, null=True, verbose_name='重定向')
    perm = models.CharField(max_length=200, blank=True, null=True, verbose_name='权限标识')
    keepAlive = models.BooleanField(blank=True, null=True, verbose_name='是否缓存')
    alwaysShow = models.BooleanField(blank=True, null=True, verbose_name='是否一直显示')
    params = models.JSONField(default=list, verbose_name='参数')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父菜单')
    desc = models.CharField(max_length=30, blank=True, null=True, verbose_name='权限描述')

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'system_permissions'
        verbose_name = '权限'
        verbose_name_plural = verbose_name
        ordering = ['sort']


class Roles(BaseModel):
    """
    角色
    """
    name = models.CharField(max_length=32, unique=True, verbose_name='角色')
    code = models.CharField(max_length=32, blank=True, null=True, verbose_name='角色编码')
    permissions = models.ManyToManyField(Permissions, db_table='system_roles_to_system_permissions',
                                         blank=True, verbose_name='权限')
    # menus = models.ManyToManyField(Menus, db_table='system_roles_to_system_menus', blank=True, verbose_name='菜单')
    status = models.IntegerField(default=1, verbose_name='状态')
    sort = models.IntegerField(default=0, verbose_name='排序')
    is_default = models.IntegerField(default=0, verbose_name="是否默认角色（新用户自动分配）")
    desc = models.CharField(max_length=50, blank=True, default='', verbose_name='描述')

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'system_roles'
        verbose_name = '角色'
        verbose_name_plural = verbose_name
        ordering = ['sort']


class Departments(BaseModel):
    """
    组织架构 部门
    """
    name = models.CharField(max_length=32, verbose_name='部门')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父部门')
    status = models.IntegerField(default=1, verbose_name='状态')
    sort = models.IntegerField(default=0, verbose_name='排序')
    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'system_departments'
        verbose_name = '部门'
        verbose_name_plural = verbose_name
        ordering = ['sort']


class Users(AbstractUser):
    """
    用户
    """
    gender_choices = (
        (0, '保密'),
        (1, '男'),
        (2, '女')
    )

    name = models.CharField(max_length=20, default='', blank=True, verbose_name='真实姓名')
    mobile = models.CharField(max_length=11, unique=True, null=True, blank=True, default=None, verbose_name='手机号码')
    image = models.ImageField(upload_to=user_avatar_path, default='avatar/default.png', blank=True, verbose_name='头像')
    roles = models.ManyToManyField(Roles, db_table='system_users_to_system_roles', blank=True,
                                   verbose_name='角色')
    dept = models.ForeignKey(Departments, null=True, blank=True, on_delete=models.SET_NULL,
                             verbose_name='直属部门')
    gender = models.IntegerField(default=0, choices=gender_choices, verbose_name='性别')
    is_active = models.IntegerField(default=1, verbose_name='是否激活')

    class Meta:
        db_table = 'system_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.username

    def _get_user_permissions(self):
        # 获取用户权限
        perms = list(filter(None, set(self.roles.values_list('permissions__perm', flat=True))))
        if 'admin' in self.roles.values_list('name', flat=True):
            perms.append('admin')
        return perms

    def get_menus(self):
        # 获取用户菜单
        menus = Permissions.objects.filter(type__in=['CATALOG', 'MENU', 'EXTLINK'],
                                           roles__in=self.roles.all()).distinct().order_by('sort')

        # 将菜单转换为树形结构
        menu_dict = {}
        menu_list = []

        # 先将所有菜单放入字典
        for menu in menus:
            # 先创建基础菜单字典
            menu_item = {
                'path': menu.route_path,
                'component': menu.component if menu.component else 'Layout',
                'name': menu.route_name if menu.route_name else menu.route_path,
                'meta': {
                    'title': menu.name,
                    'icon': menu.icon if menu.icon else '',
                    'hidden': False if menu.visible else True,
                    'alwaysShow': False if menu.alwaysShow is None else menu.alwaysShow,
                    'params': None if menu.params is None else menu.params,
                    'keepAlive': False if menu.keepAlive is None else menu.keepAlive,
                },
                'children': []
            }

            # 只有当redirect有值时才添加该字段
            if menu.redirect:
                menu_item['redirect'] = menu.redirect

            menu_dict[menu.id] = menu_item

        # 构建树形结构
        for menu in menus:
            if menu.parent_id is None:
                # 根菜单直接加入列表
                menu_list.append(menu_dict[menu.id])
            else:
                # 子菜单添加到父菜单的children中
                if menu.parent_id in menu_dict:
                    menu_dict[menu.parent_id]['children'].append(menu_dict[menu.id])

        # 移除空的children字段
        def remove_empty_children(menu_items):
            for item in menu_items:
                if 'children' in item and len(item['children']) == 0:
                    del item['children']
                elif 'children' in item and len(item['children']) > 0:
                    remove_empty_children(item['children'])

        remove_empty_children(menu_list)
        return menu_list

    def get_user_info(self):
        # 获取用户信息
        user_info = {
            'id': self.pk,
            'name': self.name,
            'username': self.username,
            # 'gender': self.gender,
            'avatar': '/media/' + str(self.image),
            'email': self.email,
            'perms': self._get_user_permissions(),
            'roles': json.dumps(list(self.roles.values_list('name', flat=True))),
            'deptName': self.dept.name if self.dept else '',
            'roleNames': '、'.join(list(self.roles.values_list('name', flat=True))),
            'mobile': '' if self.mobile is None else self.mobile,
            'gender': self.gender,
        }
        return user_info


class Dicts(BaseModel):
    """
    字典
    """
    dict_code = models.CharField(max_length=32, unique=True, verbose_name='字典编码')
    name = models.CharField(max_length=32, unique=True, verbose_name='字典名称')
    status = models.IntegerField(default=1, verbose_name='排序')
    remark = models.CharField(max_length=50, blank=True, default='', verbose_name='备注')

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'system_dicts'
        verbose_name = '字典'
        verbose_name_plural = verbose_name
        ordering = ['dict_code']


class DictItems(BaseModel):
    """
    字典项
    """
    label = models.CharField(max_length=32, verbose_name='字典项名称')
    value = models.CharField(max_length=32, verbose_name='字典编码')
    sort = models.IntegerField(default=1, verbose_name='排序')
    status = models.IntegerField(default=1, verbose_name='状态')
    tag_type = models.CharField(max_length=32, blank=True, null=True, verbose_name='标签类型')
    dict = models.ForeignKey(Dicts, on_delete=models.CASCADE, verbose_name='字典')

    objects = models.Manager()

    def __str__(self):
        return self.label

    class Meta:
        db_table = 'system_dict_items'
        verbose_name = '字典项'
        verbose_name_plural = verbose_name
        ordering = ['dict', 'sort']