from django.conf.urls import url
from juser.views import (
    group_list, group_add, group_del, group_edit, user_list, user_detail, profile,
    user_add, change_info, user_edit, user_test, user_departure, portrait_userupload
)

urlpatterns = [
    url(r'^department/list/$', group_list, name='user_group_list'),
    url(r'^department/add/$', group_add, name='user_group_add'),
    url(r'^department/del/$', group_del, name='user_group_del'),
    url(r'^department/edit/$', group_edit, name='user_group_edit'),
    url(r'^employees/list/$', user_list, name='user_list'),
    url(r'^mydetail/detail/$', user_detail, name='user_detail'),
    url(r'^user/profile/$', profile, name='user_profile'),
    url(r'^employees/add/$', user_add, name='user_add'),
    url(r'^user/update/$', change_info, name='user_update'),
    url(r'^employees/edit/$', user_edit, name='user_edit'),
    url(r'^employees/test/$', user_test, name='user_test'),
    url(r'^employees/departure/$', user_departure, name='user_departure'),
    url(r'^portrait/userupload/$', portrait_userupload, name='portrait_userupload'),
    ]
