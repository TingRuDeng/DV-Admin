# coding: utf-8

# from jasset.models import asset, AssetRecord
from juser.models import User
import datetime


# 最近预入职员工
def get_recent_join_user(day):
    now = datetime.datetime.now()
    time_line = now + datetime.timedelta(days=day)
    user_group = User.objects.filter(entry_time__lte=time_line, is_active=True, is_staff=False).order_by('-entry_time')
    # result = {}
    # for user_obj in user_group:
    #     result[user_obj.name] = user_obj.entry_time
    return user_group


# 最近入职员工
def get_recent_entry_user(day):
    now = datetime.datetime.now()
    time_line = now - datetime.timedelta(days=day)
    user_group = User.objects.filter(entry_time__gte=time_line, is_active=True, is_staff=True).order_by('-entry_time')
    # result = {}
    # for user_obj in user_group:
    #     result[user_obj.name] = user_obj.entry_time
    return user_group


# 最近离职员工
def get_recent_leave_user(day):
    now = datetime.datetime.now()
    time_line = now - datetime.timedelta(days=day)
    user_group = User.objects.filter(departure_time__gte=time_line).order_by('-departure_time')
    # result = {}
    # for user_obj in user_group:
    #     result[user_obj.name] = user_obj.departure_time
    return user_group


# 近期采购列表
def get_recent_buy_asset(day):
    now = datetime.datetime.now()
    time_line = now - datetime.timedelta(days=day)
    asset_group = asset.objects.filter(warehouse_time__gte=time_line).order_by('-warehouse_time')
    # result = {}
    # for asset_obj in asset_group:
    #     result[asset_obj.name] = asset_obj.warehouse_time
    return asset_group


# 最近变更记录
def get_recent_change_log(times):
    # log_group = AssetRecord.objects.order_by("alert_time")[-times:]
    log_group = AssetRecord.objects.all().order_by("-alert_time")
    log_group = [i for i in log_group][:times]
    # result = {}
    # for log_obj in log_group:
    #     result[log_obj.at.sn] = log_obj.content
    return log_group


def get_recent_login(day):
    now = datetime.datetime.now()
    time_line = now - datetime.timedelta(days=day)
    user_group = User.objects.filter(last_login__gte=time_line)
    return user_group