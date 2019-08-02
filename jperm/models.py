# coding: utf-8

from django.db import models
from juser.models import User, role


class menu(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'页面code')
    url = models.CharField(max_length=30, blank=True, null=True, verbose_name=u'菜单url')
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name=u'菜单名字')
    parent = models.ForeignKey('menu',
                               related_name='lower_menu',
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True,
                               verbose_name=u'上级菜单')
    icon = models.CharField(max_length=30, blank=True, null=True, verbose_name=u'菜单图标')

    def __unicode__(self):
        return self.name


class menu_permission(models.Model):
    id = models.AutoField(primary_key=True)
    menu = models.ForeignKey(menu, related_name='role_menu_id', on_delete=models.CASCADE)
    role = models.ForeignKey(role, related_name='role_permission_id', on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.menu


# 邮件模板
class Email_template(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name=u'模板名称')
    subject = models.CharField(max_length=20, default='', verbose_name=u'邮件标题')
    template_path = models.CharField(max_length=50, default='', verbose_name=u'邮件模板')
    # from_email = models.EmailField(max_length=30,blank=True, null=True, verbose_name=u'发件人地址')
    # to_email = models.CharField(max_length=200,blank=True, null=True, verbose_name=u'收件人地址')
    to_email = models.ManyToManyField(User, related_name='email_user', verbose_name=u'收件人')
    email_host = models.CharField(max_length=30, blank=True, null=True, verbose_name=u'邮箱服务器地址')
    email_port = models.CharField(max_length=30, blank=True, null=True, verbose_name=u'邮箱服务器端口')
    email_host_user = models.CharField(max_length=30, blank=True, null=True, verbose_name=u'发件人账号')
    email_host_password = models.CharField(max_length=30, blank=True, null=True, verbose_name=u'发件人密码')

    def __unicode__(self):
        return self.subject


class PermLog(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100, null=True, blank=True, default='')
    results = models.CharField(max_length=1000, null=True, blank=True, default='')
    is_success = models.BooleanField(default=False)
    is_finish = models.BooleanField(default=False)


class PermSudo(models.Model):
    name = models.CharField(max_length=100, unique=True)
    date_added = models.DateTimeField(auto_now=True)
    commands = models.TextField()
    comment = models.CharField(max_length=100, null=True, blank=True, default='')

    def __unicode__(self):
        return self.name


class PermRole(models.Model):
    name = models.CharField(max_length=100, unique=True)
    comment = models.CharField(max_length=100, null=True, blank=True, default='')
    password = models.CharField(max_length=512)
    key_path = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now=True)
    sudo = models.ManyToManyField(PermSudo, related_name='perm_role')

    def __unicode__(self):
        return self.name
