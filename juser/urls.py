from django.conf.urls import patterns, url
from juser.views import *

urlpatterns = patterns('juser.views',
                       url(r'^department/list/$', group_list, name='user_group_list'),
                       url(r'^department/add/$', group_add, name='user_group_add'),
                       url(r'^department/del/$', group_del, name='user_group_del'),
                       url(r'^department/edit/$', group_edit, name='user_group_edit'),

                       url(r'^employees/list/$', user_list, name='user_list'),
                       url(r'^mydetail/detail/$', user_detail, name='user_detail'),
                       url(r'^user/profile/$', profile, name='user_profile'),
                       url(r'^employees/add/$', user_add, name='user_add'),
                       # url(r'^user/add_batch/$', user_add_batch, name='user_add_batch'),
                       # url(r'^user/upload/$', user_upload, name='user_upload'),
                       url(r'^user/update/$', change_info, name='user_update'),
                       url(r'^employees/edit/$', user_edit, name='user_edit'),
                       url(r'^employees/test/$', user_test, name='user_test'),
                       url(r'^employees/departure/$', user_departure, name='user_departure'),

                       # oa interfaces
                       # url(r'^userprivate/userpic/$', get_user_pic, name='get_user_pic'),
                       # url(r'^userprivate/upload/$', userprivate_upload, name='userprivate_upload'),
                       # url(r'^userprivate/work_age/$', get_working_age, name='get_working_age'),

                       # url(r'^induction/list$', user_induction_list, name='user_induction_list'),
                       # url(r'^induction/email', 'induction_email', name='induction_email'),
                       # url(r'^user/induction/$', user_induction, name='user_induction'),
                       # url(r'^positive/userpositive/$', user_positive, name='user_positive'),
                       # url(r'^user/termination/$', user_termination, name='user_termination'),
                       url(r'^portrait/list/$', portrait_list, name='portrait_list'),
                       url(r'^portrait/userupload/$', portrait_userupload, name='portrait_userupload'),
                       )
