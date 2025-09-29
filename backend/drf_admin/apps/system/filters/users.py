# -*- coding: utf-8 -*-

import django_filters
from drf_admin.common.models import get_child_ids
from drf_admin.apps.system.models import Departments, Users


class UsersFilter(django_filters.rest_framework.FilterSet):
    """自定义用户管理过滤器"""
    dept = django_filters.rest_framework.NumberFilter(method='dept_service_filter')

    class Meta:
        model = Users
        fields = ['is_active', 'dept']

    def dept_service_filter(self, queryset, name, value):
        """过滤该部门及所有子部门下的用户"""
        return queryset.filter(dept_id__in=get_child_ids(value, Departments))