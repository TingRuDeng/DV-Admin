# coding: utf-8

from django.db.models.query import QuerySet
from webserver.api import *
from jperm.models import PermRole, menu, menu_permission


def list_fomat(objs):
    f_list = []
    for i in objs:
        f_list.append(int(i))
    return f_list


def diff_list(list_a, list_b):
    list_a = list_fomat(list_a)
    list_b = list_fomat(list_b)
    d_list = list(set(list_a).difference(set(list_b)))
    return d_list


def role_add_permission(role_obj,menu_list):
    for menu_id in menu_list:
        menu_obj = get_object(menu, id=menu_id)
        if menu_obj:
            menu_permission(menu=menu_obj, role=role_obj).save()
    return True


def role_del_permission(role_obj,menu_list):
    for menu_id in menu_list:
        menu_obj = get_object(menu, id=menu_id)
        if menu_obj:
            menu_permission.objects.get(menu=menu_obj, role=role_obj).delete()
    return True


def role_update_permission(role_obj, menu_list_old, menu_list_new):
    # menu_list_old = list_fomat(menu_list_old)
    # menu_list_new = list_fomat(menu_list_new)
    add_menu = diff_list(menu_list_new, menu_list_old)
    del_menu = diff_list(menu_list_old,menu_list_new)
    if add_menu:
        role_add_permission(role_obj,add_menu)
    if del_menu:
        role_del_permission(role_obj,del_menu)

    return True


def user_add_role(role_id,user_list):
    for user_id in user_list:
        if user_id:
            User.objects.filter(id=user_id).update(role_id=role_id)
    return True


def user_del_role(role_id, user_list):
    for user_id in user_list:
        if user_id:
            User.objects.filter(id=user_id).update(role_id=1)
    return True


def user_update_role(role_id, user_list_old, user_list_new):
    add_user = diff_list(user_list_new, user_list_old)
    del_user = diff_list(user_list_old, user_list_new)
    if add_user:
        user_add_role(role_id, add_user)
    if del_user:
        user_del_role(role_id, del_user)


def user_have_perm(user, asset):
    user_perm_all = get_group_user_perm(user)
    user_assets = user_perm_all.get('asset').keys()
    if asset in user_assets:
        return user_perm_all.get('asset').get(asset).get('role')
    else:
        return []


def gen_resource(ob, perm=None):
    """
    ob为用户或资产列表或资产queryset, 如果同时输入用户和{'role': role1, 'asset': []}，则获取用户在这些资产上的信息
    生成MyInventory需要的 resource文件
    """
    res = []
    if isinstance(ob, dict):
        role = ob.get('role')
        asset_r = ob.get('asset')
        user = ob.get('user')
        if not perm:
            perm = get_group_user_perm(user)

        if role:
            roles = perm.get('role', {}).keys()  # 获取用户所有授权角色
            if role not in roles:
                return {}

            role_assets_all = perm.get('role').get(role).get('asset')  # 获取用户该角色所有授权主机
            assets = set(role_assets_all) & set(asset_r)  # 获取用户提交中合法的主机

            for asset in assets:
                asset_info = get_asset_info(asset)
                role_key = get_role_key(user, role)
                info = {'hostname': asset.hostname,
                        'ip': asset.ip,
                        'port': asset_info.get('port', 22),
                        'ansible_ssh_private_key_file': role_key,
                        'username': role.name,
                        # 'password': CRYPTOR.decrypt(role.password)
                       }

                if os.path.isfile(role_key):
                    info['ssh_key'] = role_key

                res.append(info)
        else:
            for asset, asset_info in perm.get('asset').items():
                if asset not in asset_r:
                    continue
                asset_info = get_asset_info(asset)
                try:
                    role = sorted(list(perm.get('asset').get(asset).get('role')))[0]
                except IndexError:
                    continue

                role_key = get_role_key(user, role)
                info = {'hostname': asset.hostname,
                        'ip': asset.ip,
                        'port': asset_info.get('port', 22),
                        'username': role.name,
                        'password': CRYPTOR.decrypt(role.password),
                        }
                if os.path.isfile(role_key):
                    info['ssh_key'] = role_key

                res.append(info)

    elif isinstance(ob, User):
        if not perm:
            perm = get_group_user_perm(ob)

        for asset, asset_info in perm.get('asset').items():
            asset_info = get_asset_info(asset)
            info = {'hostname': asset.hostname, 'ip': asset.ip, 'port': asset_info.get('port', 22)}
            try:
                role = sorted(list(perm.get('asset').get(asset).get('role')))[0]
            except IndexError:
                continue
            info['username'] = role.name
            info['password'] = CRYPTOR.decrypt(role.password)

            role_key = get_role_key(ob, role)
            if os.path.isfile(role_key):
                    info['ssh_key'] = role_key
            res.append(info)

    elif isinstance(ob, (list, QuerySet)):
        for asset in ob:
            info = get_asset_info(asset)
            res.append(info)
    logger.debug('生成res: %s' % res)
    return res


def get_object_list(model, id_list):
    """根据id列表获取对象列表"""
    object_list = []
    for object_id in id_list:
        if object_id:
            object_list.extend(model.objects.filter(id=int(object_id)))

    return object_list


def get_role_info(role_id, type="all"):
    """
    获取role对应的一些信息
    :param role_id: 
    :param type: 
    :return: 
    """
    # 获取role对应的授权规则
    role_obj = PermRole.objects.get(id=role_id)
    rule_push_obj = role_obj.perm_rule.all()
    # 获取role 对应的用户 和 用户组
    # 获取role 对应的主机 和主机组
    users_obj = []
    assets_obj = []
    user_groups_obj = []
    asset_groups_obj = []
    for push in rule_push_obj:
        for user in push.user.all():
            users_obj.append(user)
        for asset in push.asset.all():
            assets_obj.append(asset)
        for user_group in push.user_group.all():
            user_groups_obj.append(user_group)
        for asset_group in push.asset_group.all():
            asset_groups_obj.append(asset_group)

    if type == "all":
        return {"rules": set(rule_push_obj),
                "users": set(users_obj),
                "user_groups": set(user_groups_obj),
                "assets": set(assets_obj),
                "asset_groups": set(asset_groups_obj),
                }

    elif type == "rule":
        return set(rule_push_obj)
    elif type == "user":
        return set(users_obj)
    elif type == "user_group":
        return set(user_groups_obj)
    elif type == "asset":
        return set(assets_obj)
    elif type == "asset_group":
        return set(asset_groups_obj)
    else:
        return u"不支持的查询"


def get_role_push_host(role):
    """
    asset_pushed: {'success': push.success, 'key': push.is_public_key, 'password': push.is_password,
                   'result': push.result}
    asset_no_push: set(asset1, asset2)
    """
    # 计算该role 所有push记录 总共推送的主机
    pushs = PermPush.objects.filter(role=role)
    asset_all = Asset.objects.all()
    asset_pushed = {}
    for push in pushs:
        asset_pushed[push.asset] = {'success': push.success, 'key': push.is_public_key, 'password': push.is_password,
                                    'result': push.result}
    asset_no_push = set(asset_all) - set(asset_pushed.keys())
    return asset_pushed, asset_no_push
