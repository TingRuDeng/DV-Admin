# coding: utf-8

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserGroup(models.Model):
    name = models.CharField(max_length=80)
    parent = models.ForeignKey('UserGroup',
                               related_name='parent_group_id',
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL,
                               verbose_name=u'上级部门')
    dep_admin = models.ForeignKey('User',
                                  related_name='admin_user_id',
                                  blank=True,
                                  null=True,
                                  on_delete=models.SET_NULL,
                                  verbose_name=u'部门负责人')
    is_active = models.BooleanField(default=True, verbose_name=u'部门状态')
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return self.name


class role(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30, default='GA', blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name=u'角色名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return self.code


class User(AbstractUser):
    name = models.CharField(max_length=80, verbose_name=u'姓名')
    code = models.CharField(max_length=20, default='', verbose_name=u'员工编号')
    uuid = models.CharField(max_length=100, blank=True, null=True)
    role = models.ForeignKey(role,
                             related_name='user_role_id',
                             blank=True,
                             null=True,
                             default=1,
                             verbose_name=u'角色')
    group = models.ForeignKey('UserGroup',
                              related_name='group_id',
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              verbose_name=u'所属部门')
    job = models.CharField(max_length=30, verbose_name=u'职位', blank=True, null=True)
    parent = models.ForeignKey('User',
                               related_name='parent_user_id',
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL,
                               verbose_name=u'直属领导')
    sex = models.CharField(max_length=20, default='', blank=True, null=True, verbose_name=u'性别')
    mobile = models.CharField(max_length=20,default='', blank=True, null=True, verbose_name=u'手机')
    wechat = models.CharField(max_length=20,default='', blank=True, null=True, verbose_name=u'微信')
    departure_time = models.DateTimeField(blank=True, null=True, verbose_name=u'注销日期')
    update_time = models.DateTimeField(auto_now=True)
    portrait_address = models.CharField(max_length=80, blank=True, null=True, verbose_name=u'头像地址')

    def __unicode__(self):
        return self.name
