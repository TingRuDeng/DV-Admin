from django.conf.urls import url
from jperm.views import (
    perm_role_list, perm_role_add, perm_role_edit, role_with_user, perm_role_delete, sys_email_list, sys_email_add,
    sys_email_del,  sys_email_edit, sys_email_detail, sys_email_save, sys_email_send, user_passwd_list,
    passwd_update, passwd_update_self, get_menu_dict
)

urlpatterns = [
    url(r'^role/list/$', perm_role_list, name='role_list'),
    url(r'^role/add/$', perm_role_add, name='role_add'),
    url(r'^role/edit/$', perm_role_edit, name='role_edit'),
    url(r'^role/with/$', role_with_user, name='role_with_user'),
    url(r'^role/del/$', perm_role_delete, name='role_del'),
    url(r'^email/list$', sys_email_list, name='sys_email_list'),
    url(r'^email/add', sys_email_add, name='sys_email_add'),
    url(r'^email/del', sys_email_del, name='sys_email_del'),
    url(r'^email/edit', sys_email_edit, name='sys_email_edit'),
    url(r'^email/detail', sys_email_detail, name='sys_email_detail'),
    url(r'^email/save', sys_email_save, name='sys_email_save'),
    url(r'^email/send', sys_email_send, name='email_send'),
    url(r'^passwd/list/$', user_passwd_list, name='user_passwd_list'),
    url(r'^passwd/update', passwd_update, name='passwd_update'),
    url(r'^passwd/self/$', passwd_update_self, name='passwd_update_self'),
    url(r'^role/data', get_menu_dict, name='get_menu_dict'),
]
