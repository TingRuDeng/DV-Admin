# # coding:utf-8
# from django.conf.urls import patterns, include, url
# from jmeet.views import *
# # from django.contrib import admin
#
# urlpatterns = patterns('',
#                        url(r'^reservation/list/$', reservation_list, name='reservation_list'),
#                        url(r'^reservation/before/', source_event_before, name='source_event_before'),
#                        # url(r'^reservation/before/', businessHours_dow, name='businessHours_dow'),
#                        url(r'^reservation/after/', source_event_after, name='source_event_after'),
#                        url(r'^reservation/add/$', reservation_add, name='reservation_add'),
#                        url(r'^reservation/edit/$', reservation_edit, name='reservation_edit'),
#                        # url(r'^reservation/del/$', reservation_del, name='reservation_del'),
#                        url(r'^myres/myreservation/$', my_reservation, name='my_reservation'),
#                        url(r'^mylist/myreservation/$', my_list, name='my_list'),
#                        url(r'^myres/before/', my_event, name='my_event'),
#                        url(r'^myres/after/', other_event, name='other_event'),
#
#                        url(r'^meet/manager/$', meet_manager, name='meet_manager'),
#                        url(r'^meet/add/$', meet_add, name='meet_add'),
#                        url(r'^meet/edit/$', meet_edit, name='meet_edit'),
#                        url(r'^meet/del/$', meet_del, name='meet_del'),
#                        url(r'^meet/status/add/$', meet_status_add, name='meet_status_add'),
#
#                        # url(r'^meet/test/$', test, name='test'),
# )