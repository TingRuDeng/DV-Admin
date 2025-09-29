import datetime
from django.db.models import Q


# 例子
# class ExampleFilter(filters.FilterSet):
#     # field_name: 要过滤的模型字段的名称，支持关联查询，如bank__name
#     search_name = filters.CharFilter(field_name='name')
#
#     # 用法和`django`一样
#     # 这里会自动补全中间的双下划线
#     # lookup_expr: 过滤时使用的字段查找，如price__gte
#     min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
#     max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
#     min_year = filters.NumberFilter(field_name='release_date', lookup_expr='year__gte')
#
#     class Meta:
#         model = models.Message
#         # 对于`model`中存在的字段，可以直接指定字段名
#         fields = []


# class CardFilter(filters.FilterSet):
#     class Meta:
#         model = models.CreditCard
#         fields = ['bank', 'type', 'is_active']


# 自定义过滤方法，暂时还没用到，后面看情况
def update_queryset(queryset, search_params):
    """重写内置查询方法，实现多条件查询"""
    filter_conditions = {}
    for k, v in search_params.items():
        if v and k not in ['page', 'limit', 'type', 'ordering', 'search']:
            filter_conditions[k] = v
    if 'type' in search_params and search_params['type']:
        now_time = datetime.datetime.now()
        if search_params['type'] == 'past':
            query = Q(is_active=False) | Q(end_time__lt=now_time)
            queryset = queryset.filter(query)
        elif search_params['type'] == 'future':
            filter_conditions['start_time__gt'] = now_time
        elif search_params['type'] == 'present':
            filter_conditions['is_active'] = True
            filter_conditions['start_time__lte'] = now_time
            filter_conditions['end_time__gte'] = now_time
        elif search_params['type'] == 'now':
            # 返回已结束和正在进行中的活动列表
            filter_conditions['start_time__lte'] = now_time

    if filter_conditions:
        queryset = queryset.filter(**filter_conditions).distinct()

    # if 'search' in search_params and search_params['search']:
    #     q = Q()
    #     q.connector = 'or'
    #     q.children.append(('name__icontains', search_params['search']))
    #     q.children.append(('tail_num__icontains', search_params['search']))
    #     queryset = queryset.filter(q)
    return queryset
