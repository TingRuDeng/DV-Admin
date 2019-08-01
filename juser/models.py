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
                               verbose_name='上级部门')
    dep_admin = models.ForeignKey('User',
                                  related_name='admin_user_id',
                                  blank=True,
                                  null=True,
                                  on_delete=models.SET_NULL,
                                  verbose_name='部门负责人')
    is_active = models.BooleanField(default=True, verbose_name='部门状态')
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return self.name


# 员工位置
# class userposition(models.Model) :
#     id = models.AutoField(primary_key = True)
#     name = models.CharField(max_length=30, default='')
#
#     def __unicode__(self):
#         return self.name


class role(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30, default='GA', blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name='角色名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return self.code


class User(AbstractUser):
    name = models.CharField(max_length=80, verbose_name='姓名')
    coin_addr = models.CharField(max_length=80, null=True, blank=True, verbose_name='货币地址')
    uuid = models.CharField(max_length=100, blank=True, null=True)
    role = models.ForeignKey(role,
                             related_name='user_role_id',
                             blank=True,
                             null=True,
                             default=1,
                             verbose_name='角色')
    group = models.ForeignKey('UserGroup',
                              related_name='group_id',
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              verbose_name='所属部门')
    job = models.CharField(max_length=30, verbose_name='职位', blank=True, null=True)
    parent = models.ForeignKey('User',
                               related_name='parent_user_id',
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL,
                               verbose_name='直属领导')
    sex = models.CharField(max_length=20, default='', blank=True, null=True, verbose_name='性别')
    mobile = models.CharField(max_length=20,default='', blank=True, null=True, verbose_name='手机')
    wechat = models.CharField(max_length=20,default='', blank=True, null=True, verbose_name='微信')
    departure_time = models.DateTimeField(blank=True, null=True, verbose_name='注销日期')
    update_time = models.DateTimeField(auto_now=True)
    portrait_address = models.CharField(max_length=80, blank=True, null=True, verbose_name='头像地址')

    def __unicode__(self):
        return self.name


class AppCategory(models.Model):
    id = models.AutoField(primary_key=True)
    cate_id = models.IntegerField(null=True, db_index=True, blank=True, verbose_name='分类id')
    name = models.CharField(max_length=200, db_index=True, verbose_name='分类名')


class BrandCategory(models.Model):
    id = models.AutoField(primary_key=True)
    cate_id = models.IntegerField(null=True, db_index=True, blank=True, verbose_name='分类id')
    name = models.CharField(max_length=200, db_index=True, verbose_name='分类名')


class GameCategory(models.Model):
    id = models.AutoField(primary_key=True)
    cate_id = models.IntegerField(null=True, db_index=True, blank=True, verbose_name='分类id')
    name = models.CharField(max_length=200, db_index=True, verbose_name='分类名')


class AppTag(models.Model):
    id = models.AutoField(primary_key=True)
    tag_id = models.IntegerField(null=True, db_index=True, blank=True, verbose_name='tag id')
    name = models.CharField(max_length=200, db_index=True, verbose_name='tag 名')


class BrandTag(models.Model):
    id = models.AutoField(primary_key=True)
    tag_id = models.IntegerField(null=True, db_index=True, blank=True, verbose_name='tag id')
    name = models.CharField(max_length=200, db_index=True, verbose_name='tag名')


class GameTag(models.Model):
    id = models.AutoField(primary_key=True)
    tag_id = models.IntegerField(null=True, db_index=True, blank=True, verbose_name='tag id')
    name = models.CharField(max_length=200, db_index=True, verbose_name='tag名')


class Media(models.Model):
    id = models.AutoField(primary_key=True)
    media_id = models.IntegerField(null=True, db_index=True, blank=True, verbose_name='media id')
    name = models.CharField(max_length=200, db_index=True, verbose_name='媒体名')


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    raw_json = models.TextField(blank=True, null=True, verbose_name='原始json')
    name = models.CharField(max_length=200, verbose_name='游戏名')
    product_id = models.IntegerField(null=True, blank=True, db_index=True)
    logo = models.CharField(max_length=250, null=True, blank=True)
    c_id = models.IntegerField(null=True, blank=True)
    cname = models.CharField(max_length=250, null=True, blank=True)
    type_id = models.IntegerField(null=True, blank=True)
    cat_id = models.IntegerField(null=True, blank=True)
    cat_name = models.CharField(max_length=250, null=True, blank=True)
    ua = models.CharField(max_length=250, null=True, blank=True)
    medias = models.CharField(max_length=250, null=True, blank=True)
    media_count = models.IntegerField(null=True, blank=True)
    plannum = models.IntegerField(null=True, blank=True)
    materialnum = models.IntegerField(null=True, blank=True)
    op_company = models.CharField(max_length=250, null=True, blank=True)
    op_count = models.IntegerField(null=True, blank=True)
    day_duration = models.IntegerField(null=True, blank=True)
    add_time = models.DateField(null=True, blank=True)
    last_time = models.DateField(null=True, blank=True)
    add_time = models.CharField(max_length=250, null=True, blank=True)
    all_mtnum = models.IntegerField(null=True, blank=True)
    all_plannum = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    creative_num = models.IntegerField(null=True, blank=True)
    day_plan_avg = models.IntegerField(null=True, blank=True)
    day_mt_avg = models.IntegerField(null=True, blank=True)



class GameContent(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, related_name='get_content', blank=True, null=True, on_delete=models.SET_NULL)
    raw_json = models.TextField(blank=True, null=True, verbose_name='原始json')
    lp = models.CharField(max_length=250, null=True, blank=True)
    media = models.CharField(max_length=250, null=True, blank=True)
    ua = models.IntegerField(null=True, blank=True)
    product_logo = models.CharField(max_length=250, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    audit_time = models.DateTimeField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    materialtype = models.IntegerField(null=True, blank=True)
    last_time = models.CharField(max_length=100, null=True, blank=True)
    product_id = models.IntegerField(null=True, blank=True)
    res_id = models.IntegerField(null=True, blank=True, db_index=True)
    cat_id = models.IntegerField(null=True, blank=True, db_index=True)
    media_id = models.IntegerField(null=True, blank=True, db_index=True)
    tag_id = models.IntegerField(null=True, blank=True, db_index=True)
    logo = models.CharField(max_length=250, null=True, blank=True)
    g_id = models.IntegerField(null=True, blank=True)
    op_company_id = models.IntegerField(null=True, blank=True, db_index=True)
    op_company = models.CharField(max_length=250, null=True, blank=True)
    media_name = models.CharField(max_length=250, null=True, blank=True)
    creative_str = models.CharField(max_length=250, null=True, blank=True)
    materialurl = models.CharField(max_length=250, null=True, blank=True)
    company_id = models.IntegerField(null=True, blank=True)
    lp_type = models.IntegerField(null=True, blank=True)
    cat_name = models.CharField(max_length=250, null=True, blank=True)
    type_id = models.IntegerField(null=True, blank=True)
    tag_name = models.CharField(max_length=250, null=True, blank=True)
    showlp = models.BooleanField(default=True)
    product_name = models.CharField(max_length=250, null=True, blank=True)
    creative = models.CharField(max_length=250, null=True, blank=True)
    materialvideo = models.CharField(max_length=250, null=True, blank=True)
    size = models.CharField(max_length=250, null=True, blank=True)
    _version = models.CharField(max_length=250, null=True, blank=True)
    create_day = models.CharField(max_length=250, null=True, blank=True)
    materialtype_name = models.CharField(max_length=250, null=True, blank=True)
    ad_style = models.CharField(max_length=250, null=True, blank=True)
    add_time = models.CharField(max_length=100, null=True, blank=True)

