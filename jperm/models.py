# coding: utf-8

from django.db import models
from juser.models import User, UserGroup, role


class menu(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, blank=True, null=True, verbose_name='页面code')
    url = models.CharField(max_length=30, blank=True, null=True, verbose_name='菜单url')
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name='菜单名字')
    parent = models.ForeignKey('menu',
                               related_name='lower_menu',
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True,
                               verbose_name='上级菜单')
    icon = models.CharField(max_length=30, blank=True, null=True, verbose_name='菜单图标')

    def __unicode__(self):
        return self.name


class menu_permission(models.Model):
    id = models.AutoField(primary_key=True)
    menu = models.ForeignKey(menu, related_name='role_menu_id')
    role = models.ForeignKey(role, related_name='role_permission_id')
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.menu


# 邮件模板
class Email_template(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name='模板名称')
    subject = models.CharField(max_length=20, default='', verbose_name='邮件标题')
    template_path = models.CharField(max_length=50, default='', verbose_name='邮件模板')
    # from_email = models.EmailField(max_length=30,blank=True, null=True, verbose_name=u'发件人地址')
    # to_email = models.CharField(max_length=200,blank=True, null=True, verbose_name=u'收件人地址')
    to_email = models.ManyToManyField(User, related_name='email_user', verbose_name='收件人')
    email_host = models.CharField(max_length=30,blank=True, null=True, verbose_name='邮箱服务器地址')
    email_port = models.CharField(max_length=30,blank=True, null=True, verbose_name='邮箱服务器端口')
    email_host_user = models.CharField(max_length=30,blank=True, null=True, verbose_name='发件人账号')
    email_host_password = models.CharField(max_length=30,blank=True, null=True, verbose_name='发件人密码')

    def __unicode__(self):
        return self.subject

#
# class Task(models.Model):
#     id = models.AutoField(primary_key=True)
#     uuid = models.CharField(max_length=128, blank=True, null=True, verbose_name=u'任务ID')
#     name = models.CharField(max_length=128, blank=True, verbose_name=u'任务名称')
#     date_start = models.DateTimeField(auto_now_add=True, verbose_name=u'任务创建时间')
#     date_finished = models.DateTimeField(blank=True, null=True, verbose_name=u'任务结束时间')
#     timedelta = models.CharField(max_length=100, default=0.0, verbose_name=u'任务耗时', null=True)
#     is_finished = models.BooleanField(default=False, verbose_name=u'任务是否结束')
#     is_success = models.BooleanField(default=False, verbose_name=u'任务是否成功')
#     user = models.ForeignKey(User, null=True, blank=True, verbose_name=u'任务创建人员')
#     to_email = models.ManyToManyField(User, related_name='task_to_user', verbose_name=u'收件人')
#     success_to_email = models.ManyToManyField(User, related_name='task_to_success', verbose_name=u'接收成功的员工')
#     # to_email = models.ManyToManyField(User, verbose_name=u'接收失败的员工')
#
#     def __unicode__(self):
#         return "%s" % self.uuid


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


# class PermRule(models.Model):
#     date_added = models.DateTimeField(auto_now=True)
#     name = models.CharField(max_length=100, unique=True)
#     comment = models.CharField(max_length=100)
#     asset = models.ManyToManyField(Assets, related_name='perm_rule')
#     asset_group = models.ManyToManyField(AssetGroup, related_name='perm_rule')
#     user = models.ManyToManyField(User, related_name='perm_rule')
#     user_group = models.ManyToManyField(UserGroup, related_name='perm_rule')
#     role = models.ManyToManyField(PermRole, related_name='perm_rule')
#
#     def __unicode__(self):
#         return self.name


# class PermPush(models.Model):
#     asset = models.ForeignKey(Assets, related_name='perm_push')
#     role = models.ForeignKey(PermRole, related_name='perm_push')
#     is_public_key = models.BooleanField(default=False)
#     is_password = models.BooleanField(default=False)
#     success = models.BooleanField(default=False)
#     result = models.TextField(default='')
#     date_added = models.DateTimeField(auto_now=True)

