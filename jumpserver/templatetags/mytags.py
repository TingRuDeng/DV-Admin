# coding: utf-8

import ast

from django import template
from jumpserver.api import *
from juser.models import User, UserGroup
from urllib import parse

register = template.Library()


@register.filter(name='int2str')
def int2str(value):
    """
    int 转换为 str
    """
    return str(value)


@register.filter(name='get_role')
def get_role(user_id):
    """
    根据用户id获取用户权限
    """

    # user_role = {'SU': u'超级管理员', 'GA': u'组管理员', 'CU': u'普通用户'}
    # user = get_object(User, id=user_id)
    # if user:
    #     return user_role.get(str(user.role), u"普通用户")
    # else:
    #     return u"普通用户"
    user = get_object(User, id=user_id)
    if user:
        return user.role.name
    else:
        return "普通用户"



@register.filter(name='groups2str')
def groups2str(group_list):
    """
    将用户组列表转换为str
    """
    if len(group_list) < 3:
        return ' '.join([group.name for group in group_list])
    else:
        return '%s ...' % ' '.join([group.name for group in group_list[0:2]])


@register.filter(name='user_asset_count')
def user_asset_count(user):
    """
    返回用户权限主机的数量
    """
    assets = user.asset.all()
    asset_groups = user.asset_group.all()

    for asset_group in asset_groups:
        if asset_group:
            assets.extend(asset_group.asset_set.all())

    return len(assets)


@register.filter(name='dep_admin_get')
def dep_admin_get(user_id):
    """
    返回员工所属部门负责人
    """
    # try:
    #     if User.objects.get(id=user_id).code in ('HLJF0001','HLJF0002','HLJF0003'):
    #         return None
    # except Exception,e:
    #     logger.error(u"User.objects.get(id=user_id).code in ('HLJF0001','HLJF0002','HLJF0003')执行报错！")

    try:
        user_obj = get_object(User, id=user_id)
        if user_obj:
            group_obj = user_obj.group
        else:
            return None
        if group_obj:
            if user_id == group_obj.dep_admin_id:
                if group_obj.parent:
                    return group_obj.parent.dep_admin.name
                else:
                    return ""
            else:
                return group_obj.dep_admin.name
        else:
            return None
    except Exception as e:
        logger.error('获取员工所属部门负责人异常：%s' %e)
    # print "dep_id",dep_admin_id
    # if user_id == dep_admin_id:
    #     return user.group.parent.dep_admin.name
    # else:
    #     return user.group.dep_admin.name

    # user = User.objects.get(id=user_id)
    # name = user.group
    # print "======",name,type(name)
    #group_admin_name = name(0)
    # name = get_object(User, id=user_id)
    # asset_groups = user.asset_group.all()
    #
    # for asset_group in asset_groups:
    #     if asset_group:
    #         assets.extend(asset_group.asset_set.all())
    #
    # return name


# @register.filter(name='get_menu_all')
# def get_menu_all(code):
#     if session_menu_obj:
#         menu_obj = obj.filter(code=code)
#         url = menu_obj.menu.url
#         name = menu_obj.menu.name



@register.filter(name='user_asset_group_count')
def user_asset_group_count(user):
    """
    返回用户权限主机组的数量
    """
    return len(user.asset_group.all())


@register.filter(name='bool2str')
def bool2str(value):
    if value:
        return '在职'
    else:
        return '未激活'


@register.filter(name='user_with_status')
def user_with_status(user):
    """
    目前还未启用转正流程
    :param user: 
    :return: 
    """
    # if user.is_active:
    #     if user.is_staff:
    #         if user.positive_time:
    #             return u'在职'
    #         else:
    #             return u'试用'
    #     else:
    #         return u'预入职'
    # else:
    #     return u'离职'

    """
    现在员工状态暂时只定义在职和离职
    """
    if user.is_active:
        # if user.is_staff:
        return '正常'
        # else:
        #     return u'预入职'
    else:
        return "异常"


# @register.filter(name='get_user_surplus')
# def get_user_surplus(user):
#     return to_compute(user.pk)


@register.filter(name='res_with_status')
def res_with_status(object):
    try:
        if object.status:
            return '执行完毕'
        else:
            return '执行中'
    except Exception as e:
        logger.error('res_with_status：%s' %e)
        print(e)


@register.filter(name='bool_with_status')
def bool_with_status(str):
    try:
        if str:
            return '是'
        else:
            return '否'
    except Exception as e:
        logger.error('bool_with_status函数报错：%s' %e)
        print(e)


@register.filter(name='members_count')
def members_count(group_id):
    """统计部门下员工数量"""

    #判断当前部门是否有下级部门，如果有则统计进部门人数中
    group = get_object(UserGroup, id=group_id)
    sub_deps = UserGroup.objects.filter(parent=group)

    if group:
        #获取本部门下员工人数
        dep_user_num = User.objects.filter(group_id=group_id, is_active=1, is_staff=1).count()
        if sub_deps:
            #获取本部门下级部门员工人数，相加统计并返回
            dep_list = [i.id for i in sub_deps]
            sub_user_num = User.objects.filter(group_id__in=dep_list, is_active=1, is_staff=1).count()
            return int(dep_user_num) + int(sub_user_num)
        else:
            return int(dep_user_num)
    else:
        return 0


@register.filter(name='to_user_name')
def to_user_name(username):
    try:
        user = User.objects.filter(username=username)
        if user:
            user = user[0]
            return user.name
    except:
        return username

@register.filter(name='to_name')
def to_name(user_id):
    """user id 转位用户名称"""
    try:
        user = User.objects.filter(id=int(user_id))
        if user:
            user = user[0]
            return user.name
    except:
        return '非法用户'


@register.filter(name='to_role_name')
def to_role_name(role_id):
    """role_id 转变为角色名称"""
    role_dict = {'0': '普通用户', '1': '组管理员', '2': '超级管理员'}
    return role_dict.get(str(role_id), '未知')


@register.filter(name='to_avatar')
def to_avatar(role_id='0'):
    """不同角色不同头像"""
    role_dict = {'0': 'user', '1': 'admin', '2': 'root'}
    return role_dict.get(str(role_id), 'user')


@register.filter(name='result2bool')
def result2bool(result=''):
    """将结果定向为结果"""
    result = eval(result)
    unreachable = result.get('unreachable', [])
    failures = result.get('failures', [])

    if unreachable or failures:
        return '<b style="color: red">失败</b>'
    else:
        return '<b style="color: green">成功</b>'


@register.filter(name='rule_member_count')
def rule_member_count(instance, member):
    """
    instance is a rule object,
    use to get the number of the members
    :param instance:
    :param member:
    :return:
    """
    member = getattr(instance, member)
    counts = member.all().count()
    return str(counts)


@register.filter(name='rule_member_name')
def rule_member_name(instance, member):
    """
    instance is a rule object,
    use to get the name of the members
    :param instance:
    :param member:
    :return:
    """
    member = getattr(instance, member)
    names = member.all()

    return names


@register.filter(name='user_which_groups')
def user_which_group(user, member):
    """
    instance is a user object,
    use to get the group of the user
    :param instance:
    :param member:
    :return:
    """
    member = getattr(user, member)
    names = [members.name for members in member.all()]

    return ','.join(names)


@register.filter(name='asset_which_groups')
def asset_which_group(asset, member):
    """
    instance is a user object,
    use to get the group of the user
    :param instance:
    :param member:
    :return:
    """
    member = getattr(asset, member)
    names = [members.name for members in member.all()]

    return ','.join(names)


@register.filter(name='group_str2')
def groups_str2(group_list):
    """
    将用户组列表转换为str
    """
    if len(group_list) < 3:
        return ' '.join([group.name for group in group_list])
    else:
        return '%s ...' % ' '.join([group.name for group in group_list[0:2]])


@register.filter(name='str_to_list')
def str_to_list(info):
    """
    str to list
    """
    # print ast.literal_eval(info), type(ast.literal_eval(info))
    return ast.literal_eval(info)


@register.filter(name='str_to_dic')
def str_to_dic(info):
    """
    str to list
    """
    if '{' in info:
        info_dic = iter(list(ast.literal_eval(info).items()))
    else:
        info_dic = {}
    return info_dic


@register.filter(name='str_to_code')
def str_to_code(char_str):
    if char_str:
        return char_str
    else:
        return '空'


@register.filter(name='ip_str_to_list')
def ip_str_to_list(ip_str):
    """
    ip str to list
    """
    return ip_str.split(',')


@register.filter(name='key_exist')
def key_exist(username):
    """
    ssh key is exist or not
    """
    if os.path.isfile(os.path.join(KEY_DIR, 'user', username+'.pem')):
        return True
    else:
        return False


@register.filter(name='check_role')
def check_role(asset_id, user):
    """
    ssh key is exist or not
    """
    return user


@register.filter(name='role_contain_which_sudos')
def role_contain_which_sudos(role):
    """
    get role sudo commands
    """
    sudo_names = [sudo.name for sudo in role.sudo.all()]
    return ','.join(sudo_names)


@register.filter(name='role_which_permission')
def role_which_permission(role):
    """
    get role sudo commands
    """
    role_names = [role_list.menu.name for role_list in role.role_permission_id.all()]
    return ','.join(role_names)


@register.filter(name='get_push_info')
def get_push_info(push_id, arg):
    push = get_object(PermPush, id=push_id)
    if push and arg:
        if arg == 'asset':
            return [asset.hostname for asset in push.asset.all()]
        if arg == 'asset_group':
            return [asset_group.name for asset_group in push.asset_group.all()]
        if arg == 'role':
            return [role.name for role in push.role.all()]
    else:
        return []


@register.filter(name='get_cpu_core')
def get_cpu_core(cpu_info):
    cpu_core = cpu_info.split('* ')[1] if cpu_info and '*' in cpu_info else cpu_info
    return cpu_core


@register.filter(name='get_disk_info')
def get_disk_info(disk_info):
    try:
        disk_size = 0
        if disk_info:
            disk_dic = ast.literal_eval(disk_info)
            for disk, size in list(disk_dic.items()):
                disk_size += size
            disk_size = int(disk_size)
        else:
            disk_size = ''
    except Exception:
        disk_size = disk_info
    return disk_size


# @register.filter(name='user_perm_asset_num')
# def user_perm_asset_num(user_id):
#     user = get_object(User, id=user_id)
#     if user:
#         # user_perm_info = get_group_user_perm(user)
#         # return len(user_perm_info.get('asset').keys())
#     else:
#         return 0


@register.filter(name='get_asset_inventory')
def get_asset_inventory(asset_type_id):
    try:
        asset_inventory_num = asset.objects.filter(asset_type_id=asset_type_id, status_id=1).count()
        return asset_inventory_num

    except Exception as e:
        print(("===",e))
        return 0


@register.filter(name='week_to_ch')
def week_to_ch(num):
    num = int(num.strip())
    if num == 1:
        return "星期一"
    elif num == 2:
        return "星期二"
    elif num == 3:
        return "星期三"
    elif num == 4:
        return "星期四"
    elif num == 5:
        return "星期五"
    elif num == 6:
        return "星期六"
    else:
        return "星期日"


@register.filter(name='leave_to_num')
def leave_to_num(num):
    if num:
        if int(num) == 0:
            return 0
        else:
            return float(num)/2
    else:
        return 0


@register.filter(name='users_to_list')
def users_to_list(all):
    """
    当存在多对多关系时，返回用户列表
    :param all: 
    :return: 
    """
    user_list = []
    user_list = [user.name for user in all]
    return '、'.join(user_list)

@register.filter(name='avg_cost')
def avg_cost(act_obj):
    """
    当存在多对多关系时，返回用户列表
    :param all:
    :return:
    """
    cost = act_obj.cost
    num = act_obj.participants.all().count()
    return round(float(cost)/num,2)


@register.filter(name='purchase_cost')
def purchase_cost(value, arg):
    return value * arg


@register.filter(name='leave_days')
def leave_days(number):
    return int((number / 2.0) * 10) / 10.0


# @register.filter(name='get_match_status')
# def get_match_status(match_obj):
#     if (datetime.datetime.now()<match_obj.time):
#         return '<a href="/jcoin/match/bid?matchid=%s" class="btn btn-sm btn-warning "> 投注 </a>' %(match_obj.id)
#     elif (match_obj.home_score is not None):
#         return u"已结算"
#     else :
#         return u"等待结果"

#
# @register.filter(name='get_match_rate')
# def get_match_rate(match_obj, bet_obj):
#     rate = cal_match_rate(match_obj, bet_obj)
#     return round(float(rate)/100, 2)


@register.filter(name='rate_format')
def rate_format(rate):
    return round(float(rate)/100, 2)


@register.filter(name='down_file')
def down_file(mail_obj):
    content = ''
    if mail_obj.file_name:
        f_list = mail_obj.file_name.split(',')
        for f in f_list:
            f_name = '/static/file/%s' % mail_obj.mail_id + '/' + f.strip()
            content += '<a href="%s" target="_blank">%s</a><br/>' % (f_name, f.strip())
    return content
