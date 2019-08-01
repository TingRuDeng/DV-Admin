# coding:utf-8

from django.conf.urls import url
from jlog.views import *

urlpatterns = [
               url(r'^list/(\w+)/$', log_list, name='log_list'),
               url(r'^log/bid/$', log_bid, name='log_bid'),
               url(r'^log/winbid/$', log_winbid, name='log_winbid'),
                url(r'^log/chain/$', log_chain, name='log_chain'),
               url(r'^detail/(\w+)/$', log_detail, name='log_detail'),
               url(r'^info/(\w+)/$', log_info, name='log_info'),
               url(r'^history/$', log_history, name='log_history'),
               url(r'^log_kill/', log_kill, name='log_kill'),
               url(r'^record/$', log_record, name='log_record'),
               ]
