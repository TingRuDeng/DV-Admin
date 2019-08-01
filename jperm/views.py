# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from django.forms import model_to_dict

from jperm.perm_api import *
from jperm.forms import *
from webserver.api import my_render, get_object
# from juser.urls import user_induction_list


# 设置PERM APP Log
from webserver.api import logger


# @require_role('super')
# def perm_rule_list(request):
#     """
#     list rule page
#     授权规则列表
#     """
#     # 渲染数据
#     header_title, path1, path2 = "角色分配", "权限管理", "角色分配"
#     # 获取所有规则
#     role_list = role.objects.exclude(id=1)
#     role_id = request.GET.get('id')
#     # TODO: 搜索和分页
#     keyword = request.GET.get('search', '')
#     # if role_id:
#     #     rules_list = rules_list.filter(id=rule_id)
#     #
#     # if keyword:
#     #     rules_list = role.filter(Q(name__icontains=keyword))
#
#     rules_list, p, roles, page_range, current_page, show_first, show_end = pages(role_list, request)
#
#     return my_render('jperm/perm_rule_list.html', locals(), request)


# @require_role('super')
# def perm_rule_detail(request):
#     """
#     rule detail page
#     授权详情
#     """
#     # 渲染数据
#     header_title, path1, path2 = "授权规则", "规则管理", "规则详情"
#
#     # 根据rule_id 取得rule对象
#     try:
#         if request.method == "GET":
#             rule_id = request.GET.get("id")
#             if not rule_id:
#                 raise ServerError("Rule Detail - no rule id get")
#             rule_obj = PermRule.objects.get(id=rule_id)
#             user_obj = rule_obj.user.all()
#             user_group_obj = rule_obj.user_group.all()
#             asset_obj = rule_obj.asset.all()
#             asset_group_obj = rule_obj.asset_group.all()
#             roles_name = [role.name for role in rule_obj.role.all()]
#
#             # 渲染数据
#             roles_name = ','.join(roles_name)
#             rule = rule_obj
#             users = user_obj
#             user_groups = user_group_obj
#             assets = asset_obj
#             asset_groups = asset_group_obj
#     except ServerError, e:
#         logger.warning(e)
#
#     return my_render('jperm/perm_rule_detail.html', locals(), request)


# @require_role('super')
# def perm_rule_add(request):
#     """
#     add rule page
#     添加授权
#     """
#     # 渲染数据
#     header_title, path1, path2 = "授权规则", "规则管理", "添加规则"
#
#     # 渲染数据, 获取所有 用户,用户组,资产,资产组,用户角色, 用于添加授权规则
#     users = User.objects.all()
#     user_groups = UserGroup.objects.all()
#     assets = Assets.objects.all()
#     asset_groups = AssetGroup.objects.all()
#     roles = PermRole.objects.all()
#
#     if request.method == 'POST':
#         # 获取用户选择的 用户,用户组,资产,资产组,用户角色
#         users_select = request.POST.getlist('user', [])  # 需要授权用户
#         user_groups_select = request.POST.getlist('user_group', [])  # 需要授权用户组
#         assets_select = request.POST.getlist('asset', [])  # 需要授权资产
#         asset_groups_select = request.POST.getlist('asset_group', [])  # 需要授权资产组
#         roles_select = request.POST.getlist('role', [])  # 需要授权角色
#         rule_name = request.POST.get('name')
#         rule_comment = request.POST.get('comment')
#
#         try:
#             rule = get_object(PermRule, name=rule_name)
#
#             if rule:
#                 raise ServerError(u'授权规则 %s 已存在' % rule_name)
#
#             if not rule_name or not roles_select:
#                 raise ServerError(u'系统用户名称和规则名称不能为空')
#
#             # 获取需要授权的主机列表
#             assets_obj = [Asset.objects.get(id=asset_id) for asset_id in assets_select]
#             asset_groups_obj = [AssetGroup.objects.get(id=group_id) for group_id in asset_groups_select]
#             group_assets_obj = []
#             for asset_group in asset_groups_obj:
#                 group_assets_obj.extend(list(asset_group.asset_set.all()))
#             calc_assets = set(group_assets_obj) | set(assets_obj)  # 授权资产和资产组包含的资产
#
#             # 获取需要授权的用户列表
#             users_obj = [User.objects.get(id=user_id) for user_id in users_select]
#             user_groups_obj = [UserGroup.objects.get(id=group_id) for group_id in user_groups_select]
#
#             # 获取授予的角色列表
#             roles_obj = [PermRole.objects.get(id=role_id) for role_id in roles_select]
#             need_push_asset = set()
#
#             for role in roles_obj:
#                 asset_no_push = get_role_push_host(role=role)[1]  # 获取某角色已经推送的资产
#                 need_push_asset.update(set(calc_assets) & set(asset_no_push))
#                 if need_push_asset:
#                     raise ServerError(u'没有推送系统用户 %s 的主机 %s'
#                                       % (role.name, ','.join([asset.hostname for asset in need_push_asset])))
#
#             # 仅授权成功的，写回数据库(授权规则,用户,用户组,资产,资产组,用户角色)
#             rule = PermRule(name=rule_name, comment=rule_comment)
#             rule.save()
#             rule.user = users_obj
#             rule.user_group = user_groups_obj
#             rule.asset = assets_obj
#             rule.asset_group = asset_groups_obj
#             rule.role = roles_obj
#             rule.save()
#
#             msg = u"添加授权规则：%s" % rule.name
#             return HttpResponseRedirect(reverse('rule_list'))
#         except ServerError, e:
#             error = e
#     return my_render('jperm/perm_rule_add.html', locals(), request)


# @require_role('super')
# def perm_rule_edit(request):
#     """
#     edit rule page
#     """
#     # 渲染数据
#     header_title, path1, path2 = "授权规则", "规则管理", "添加规则"
#
#     # 根据rule_id 取得rule对象
#     rule_id = request.GET.get("id")
#     rule = get_object(PermRule, id=rule_id)
#
#     # 渲染数据, 获取所选的rule对象
#
#     users = User.objects.all()
#     user_groups = UserGroup.objects.all()
#     assets = Asset.objects.all()
#     asset_groups = AssetGroup.objects.all()
#     roles = PermRole.objects.all()
#
#     if request.method == 'POST' and rule_id:
#         # 获取用户选择的 用户,用户组,资产,资产组,用户角色
#         rule_name = request.POST.get('name')
#         rule_comment = request.POST.get("comment")
#         users_select = request.POST.getlist('user', [])
#         user_groups_select = request.POST.getlist('user_group', [])
#         assets_select = request.POST.getlist('asset', [])
#         asset_groups_select = request.POST.getlist('asset_group', [])
#         roles_select = request.POST.getlist('role', [])
#
#         try:
#             if not rule_name or not roles_select:
#                 raise ServerError(u'系统用户和关联系统用户不能为空')
#
#             assets_obj = [Asset.objects.get(id=asset_id) for asset_id in assets_select]
#             asset_groups_obj = [AssetGroup.objects.get(id=group_id) for group_id in asset_groups_select]
#             group_assets_obj = []
#             for asset_group in asset_groups_obj:
#                 group_assets_obj.extend(list(asset_group.asset_set.all()))
#             calc_assets = set(group_assets_obj) | set(assets_obj)  # 授权资产和资产组包含的资产
#
#             # 获取需要授权的用户列表
#             users_obj = [User.objects.get(id=user_id) for user_id in users_select]
#             user_groups_obj = [UserGroup.objects.get(id=group_id) for group_id in user_groups_select]
#
#             # 获取授予的角色列表
#             roles_obj = [PermRole.objects.get(id=role_id) for role_id in roles_select]
#             need_push_asset = set()
#             for role in roles_obj:
#                 asset_no_push = get_role_push_host(role=role)[1]  # 获取某角色已经推送的资产
#                 need_push_asset.update(set(calc_assets) & set(asset_no_push))
#                 if need_push_asset:
#                     raise ServerError(u'没有推送系统用户 %s 的主机 %s'
#                                       % (role.name, ','.join([asset.hostname for asset in need_push_asset])))
#
#                 # 仅授权成功的，写回数据库(授权规则,用户,用户组,资产,资产组,用户角色)
#                 rule.user = users_obj
#                 rule.user_group = user_groups_obj
#                 rule.asset = assets_obj
#                 rule.asset_group = asset_groups_obj
#                 rule.role = roles_obj
#             rule.name = rule_name
#             rule.comment = rule_comment
#             rule.save()
#             msg = u"更新授权规则：%s成功" % rule.name
#
#         except ServerError, e:
#             error = e
#
#     return my_render('jperm/perm_rule_edit.html', locals(), request)


# @require_role('super')
# def perm_rule_delete(request):
#     """
#     use to delete rule
#     :param request:
#     :return:
#     """
#     if request.method == 'POST':
#         # 根据rule_id 取得rule对象
#         rule_id = request.POST.get("id")
#         rule_obj = PermRule.objects.get(id=rule_id)
#         rule_obj.delete()
#         return HttpResponse(u"删除授权规则：%s" % rule_obj.name)
#     else:
#         return HttpResponse(u"不支持该操作")


@require_role('admin', 'role_admin')
def perm_role_list(request):
    """
    list role page
    """
    # 渲染数据
    header_title, path1, path2 = "角色管理", "权限管理", "角色管理"

    # 获取所有系统角色
    roles_list = role.objects.all()
    role_id = request.GET.get('id')
    keyword = request.GET.get('search', '')
    if keyword:
        roles_list = roles_list.filter(Q(name=keyword))

    if role_id:
        roles_list = roles_list.filter(id=role_id)

    roles_list, p, roles, page_range, current_page, show_first, show_end = pages(roles_list, request)

    return my_render('jperm/perm_role_list.html', locals(), request)


@require_role('admin', 'role_admin')
def perm_role_add(request):
    """
    add role page
    """
    # 渲染数据
    header_title, path1, path2 = "新增角色", "权限管理", "新增角色"

    menu_obj = menu.objects.all()

    if request.method == "POST":
        # 获取参数： name, comment
        name = request.POST.get("role_name", "").strip()
        comment = request.POST.get("role_comment", "")
        menu_list = request.POST.getlist("menu", [])
        role_id_list = request.POST.get('role_id_list', '')
        role_id_list = role_id_list.split(',')
        all_list = []
        for menu_id in role_id_list:
            m_id = int(list(str(menu_id))[0])
            all_list.append(m_id)
            all_list.append(int(menu_id))
        all_list = list(set(all_list))
        try:
            if get_object(role, name=name):
                raise ServerError(u'系统中已存在同名角色')

            role_obj = role.objects.create(name=name, comment=comment)
            ManagerLog.objects.create(user_id=request.user.id, type='新增角色', msg=model_to_dict(role_obj))
            role_add_permission(role_obj, all_list)

            return HttpResponseRedirect(reverse('role_list'))
        except ServerError, e:
            error = e
    return my_render('jperm/perm_role_add.html', locals(), request)


@require_role('admin', 'role_admin')
def perm_role_delete(request):
    """
    delete role page
    """

    if request.method == "GET":
        try:
            # 获取参数删除的role对象
            role_id = request.GET.get("id")
            role_obj = get_object(role, id=role_id)
            if not role_obj:
                logger.warning(u"Delete Role: role_id %s not exist" % role_id)
                raise ServerError(u"role_id %s 在数据库中不存在" % role_id)
            if role_obj.code != "SU" and role_obj.code != "CU":
                user_list_id = [i.id for i in User.objects.filter(role_id=role_id)]
                for user_id in user_list_id:
                    if user_id:
                        user_obj = User.objects.filter(id=user_id)
                        ManagerLog.objects.create(user_id=request.user.id,
                                                  type=u'角色重置前',
                                                  msg=model_to_dict(user_obj[0]))
                        user_obj.update(role_id=1)
                        ManagerLog.objects.create(user_id=request.user.id,
                                                  type=u'角色重置后',
                                                  msg=model_to_dict(user_obj[0]))
                ManagerLog.objects.create(user_id=request.user.id, type='角色删除', msg=model_to_dict(role_obj))
                role_obj.delete()
        except ServerError, e:
            return HttpResponse(e)
    return HttpResponseRedirect(reverse("role_list"))


# @require_role('admin', 'role_admin')
# def perm_role_detail(request):
#     """
#     the role detail page
#         the role_info data like:
#             {'asset_groups': [],
#             'assets': [<Asset: 192.168.10.148>],
#             'rules': [<PermRule: PermRule object>],
#             '': [],
#             '': [<User: user1>]}
#     """
#     # 渲染数据
#     header_title, path1, path2 = "系统用户", "系统用户管理", "系统用户详情"
#
#     try:
#         if request.method == "GET":
#             role_id = request.GET.get("id")
#             if not role_id:
#                 raise ServerError("not role id")
#             role = get_object(PermRole, id=role_id)
#             role_info = get_role_info(role_id)
#
#             # 渲染数据
#             rules = role_info.get("rules")
#             assets = role_info.get("assets")
#             asset_groups = role_info.get("asset_groups")
#             users = role_info.get("users")
#             user_groups = role_info.get("user_groups")
#             pushed_asset, need_push_asset = get_role_push_host(get_object(PermRole, id=role_id))
#
#     except ServerError, e:
#         logger.warning(e)
#
#     return my_render('jperm/perm_role_detail.html', locals(), request)


@require_role('admin', 'role_admin')
def perm_role_edit(request):
    """
    edit role page
    """
    # 渲染数据
    header_title, path1, path2 = "角色修改", "权限管理", "角色编辑"

    role_id = request.GET.get("id")
    role_obj = role.objects.get(id=role_id)
    # menu_obj = menu.objects.all()
    menu_list_old = [str(menu_list.menu.id) for menu_list in role_obj.role_permission_id.all()]
    menu_str = ' '.join(menu_list_old)

    if request.method == "GET":
        return my_render('jperm/perm_role_edit.html', locals(), request)

    if request.method == "POST":
        # 获取 POST 数据
        name = request.POST.get("role_name", "").strip()
        comment = request.POST.get("role_comment", "")
        menu_list_new = request.POST.get("role_id_list", '')
        # if len(menu_list_new) == 0:
        #     return HttpResponseRedirect(reverse('role_list'))
        menu_list_new = menu_list_new.split(',')
        all_list = []

        try:
            for menu_id in menu_list_new:
                m_id = int(list(str(menu_id))[0])
                all_list.append(m_id)
                all_list.append(int(menu_id))

            all_list = list(set(all_list))
            role_get = get_object(role, name=name)
            
            if role_get:
                if int(role_get.id) != int(role_id):
                    raise ServerError(u'系统中已存在同名角色')

            ManagerLog.objects.create(user_id=request.user.id, type='角色信息变更前', msg=model_to_dict(role_obj))
            role_obj.name = name
            role_obj.comment = comment
            role_obj.save()
            ManagerLog.objects.create(user_id=request.user.id, type='角色信息变更后', msg=model_to_dict(role_obj))
            ManagerLog.objects.create(user_id=request.user.id, type='角色权限变更前',
                                      msg=[i.menu.name for i in menu_permission.objects.filter(role_id=role_id)])
            role_update_permission(role_obj, menu_list_old, all_list)
            ManagerLog.objects.create(user_id=request.user.id, type='角色权限变更后',
                                      msg=[i.menu.name for i in menu_permission.objects.filter(role_id=role_id)])

            return HttpResponseRedirect(reverse('role_list'))
        except ServerError, e:
            error = e
    return my_render('jperm/perm_role_edit.html', locals(), request)


@require_role('admin', 'role_admin')
def role_with_user(request):
    """
    the role push page
    """
    # 渲染数据
    header_title, path1, path2 = "角色分配", "系统权限管理", "角色分配"
    role_id = request.GET.get('id', '')
    role_obj = get_object(role, id=role_id)
    user_obj = User.objects.filter(is_active=1)
    user_list = [role_user.id for role_user in role_obj.user_role_id.all()]

    if request.method == 'POST':
        ManagerLog.objects.create(user_id=request.user.id, type='角色重新分配前',
                                  msg=[role_user.id for role_user in role_obj.user_role_id.all()])
        user_post = request.POST.getlist('user', '')
        user_update_role(role_id, user_list, user_post)
        ManagerLog.objects.create(user_id=request.user.id, type='角色重新分配后',
                                  msg=[role_user.id for role_user in role_obj.user_role_id.all()])
        return HttpResponseRedirect(reverse('role_list'))

    return my_render('jperm/perm_role_with.html', locals(), request)


# @require_role('super')
# def perm_sudo_list(request):
#     """
#     list sudo commands alias
#     :param request:
#     :return:
#     """
#     # 渲染数据
#     header_title, path1, path2 = "Sudo命令", "别名管理", "查看别名"
#
#     # 获取所有sudo 命令别名
#     sudos_list = PermSudo.objects.all()
#
#     # TODO: 搜索和分页
#     keyword = request.GET.get('search', '')
#     if keyword:
#         sudos_list = sudos_list.filter(Q(name=keyword))
#
#     sudos_list, p, sudos, page_range, current_page, show_first, show_end = pages(sudos_list, request)
#
#     return my_render('jperm/perm_sudo_list.html', locals(), request)


# @require_role('super')
# def perm_sudo_add(request):
#     """
#     list sudo commands alias
#     :param request:
#     :return:
#     """
#     # 渲染数据
#     header_title, path1, path2 = "Sudo命令", "别名管理", "添加别名"
#     try:
#         if request.method == "POST":
#             # 获取参数： name, comment
#             name = request.POST.get("sudo_name").strip().upper()
#             comment = request.POST.get("sudo_comment").strip()
#             commands = request.POST.get("sudo_commands").strip()
#
#             if not name or not commands:
#                 raise ServerError(u"sudo name 和 commands是必填项!")
#
#             pattern = re.compile(r'[\n,\r]')
#             deal_space_commands = list_drop_str(pattern.split(commands), u'')
#             deal_all_commands = map(trans_all, deal_space_commands)
#             commands = ', '.join(deal_all_commands)
#             logger.debug(u'添加sudo %s: %s' % (name, commands))
#
#             if get_object(PermSudo, name=name):
#                 error = 'Sudo别名 %s已经存在' % name
#             else:
#                 sudo = PermSudo(name=name.strip(), comment=comment, commands=commands)
#                 sudo.save()
#                 msg = u"添加Sudo命令别名: %s" % name
#     except ServerError, e:
#         error = e
#     return my_render('jperm/perm_sudo_add.html', locals(), request)


# @require_role('super')
# def perm_sudo_edit(request):
#     """
#     list sudo commands alias
#     :param request:
#     :return:
#     """
#     # 渲染数据
#     header_title, path1, path2 = "Sudo命令", "别名管理", "编辑别名"
#
#     sudo_id = request.GET.get("id")
#     sudo = PermSudo.objects.get(id=sudo_id)
#
#     try:
#         if request.method == "POST":
#             name = request.POST.get("sudo_name").upper()
#             commands = request.POST.get("sudo_commands")
#             comment = request.POST.get("sudo_comment")
#
#             if not name or not commands:
#                 raise ServerError(u"sudo name 和 commands是必填项!")
#
#             pattern = re.compile(r'[\n,\r]')
#             deal_space_commands = list_drop_str(pattern.split(commands), u'')
#             deal_all_commands = map(trans_all, deal_space_commands)
#             commands = ', '.join(deal_all_commands).strip()
#             logger.debug(u'添加sudo %s: %s' % (name, commands))
#
#             sudo.name = name.strip()
#             sudo.commands = commands
#             sudo.comment = comment
#             sudo.save()
#
#             msg = u"更新命令别名： %s" % name
#     except ServerError, e:
#         error = e
#     return my_render('jperm/perm_sudo_edit.html', locals(), request)


# @require_role('super')
# def perm_sudo_delete(request):
#     """
#     list sudo commands alias
#     :param request:
#     :return:
#     """
#     if request.method == "POST":
#         # 获取参数删除的role对象
#         sudo_id = request.POST.get("id")
#         sudo = PermSudo.objects.get(id=sudo_id)
#         # 数据库里删除记录
#         sudo.delete()
#         return HttpResponse(u"删除系统用户: %s" % sudo.name)
#     else:
#         return HttpResponse(u"不支持该操作")


# @require_role('super')
# def perm_role_recycle(request):
#     role_id = request.GET.get('role_id')
#     asset_ids = request.GET.get('asset_id').split(',')
#
#     # 仅有推送的角色才回收
#     assets = [get_object(Asset, id=asset_id) for asset_id in asset_ids]
#     recycle_assets = []
#     for asset in assets:
#         if True in [push.success for push in asset.perm_push.all()]:
#             recycle_assets.append(asset)
#     recycle_resource = gen_resource(recycle_assets)
#     task = MyTask(recycle_resource)
#     try:
#         msg_del_user = task.del_user(get_object(PermRole, id=role_id).name)
#         msg_del_sudo = task.del_user_sudo(get_object(PermRole, id=role_id).name)
#         logger.info("recycle user msg: %s" % msg_del_user)
#         logger.info("recycle sudo msg: %s" % msg_del_sudo)
#     except Exception, e:
#         logger.warning("Recycle Role failed: %s" % e)
#         raise ServerError(u"回收已推送的系统用户失败: %s" % e)
#
#     for asset_id in asset_ids:
#         asset = get_object(Asset, id=asset_id)
#         assets.append(asset)
#         role = get_object(PermRole, id=role_id)
#         PermPush.objects.filter(asset=asset, role=role).delete()
#
#     return HttpResponse('删除成功')


# @require_role('super')
# def perm_role_get(request):
#     asset_id = request.GET.get('id', 0)
#     if asset_id:
#         asset = get_object(Asset, id=asset_id)
#         if asset:
#             role = user_have_perm(request.user, asset=asset)
#             logger.debug(u'获取授权系统用户: ' + ','.join([i.name for i in role]))
#             return HttpResponse(','.join([i.name for i in role]))
#     else:
#         roles = get_group_user_perm(request.user).get('role').keys()
#         return HttpResponse(','.join(i.name for i in roles))
#
#     return HttpResponse('error')


@require_role('admin', 'role_admin')
def sys_email_list(request):
    header_title, path1, path2 = "系统设置", "邮件模板管理", "邮件模板列表"

    email_obj = Email_template.objects.all()
    return my_render('jperm/sys_email_list.html', locals(), request)


@require_role('admin', 'role_admin')
def sys_email_add(request):
    header_title, path1, path2 = "系统设置", "邮件模板管理", "新增邮件模板"

    if request.method == 'POST':
        to_email_list = request.POST.getlist('to_email_list', '')
        ef = EmailForm(request.POST)
        if ef.is_valid():
            email_obj = ef.save()
            if to_email_list:
                for emails in User.objects.filter(id__in=to_email_list):
                    email_obj.to_email.add(emails)
            return HttpResponseRedirect(reverse('sys_email_list'))
    else:
        ef = EmailForm()
        to_email = User.objects.all()
    return my_render('jperm/sys_email_add.html', locals(), request)


@require_role('admin', 'role_admin')
def sys_email_edit(request):
    header_title, path1, path2 = "系统设置", "邮件模板管理", "邮件模板编辑"

    email_id = request.GET.get('id', '')
    email_obj = get_object(Email_template, id=email_id)
    ef = EmailForm(instance=email_obj)
    to_emails = User.objects.all()
    email_selected = [emails.id for emails in email_obj.to_email.all()]
    to_email_list = []
    if request.method == 'POST':
        try:
            email_post_list = request.POST.getlist('to_email_list', '')
            ef_post = EmailForm(request.POST, instance=email_obj)
            # add_email = diff_list(email_post_list, email_selected)
            # del_email = diff_list(email_selected, email_post_list)
            if ef_post.is_valid():
                email_obj = ef_post.save()
                for emails in User.objects.filter(id__in=email_post_list):
                    to_email_list.append(emails)
                email_obj.to_email = set(to_email_list)
                email_obj.save()
                # if del_email:
                #     for emails in User.objects.filter(id__in=add_email):
                #         email_obj.to_email.remove(emails)
                # ef_save.save()
                return HttpResponseRedirect(reverse('sys_email_list'))
        except Exception, e:
            print "error=%s" % e
    return my_render('jperm/sys_email_edit.html', locals(), request)


@require_role('admin', 'role_admin')
def sys_email_del(request):
    """
    del a email
    删除邮件模板
    """
    if request.method == "GET":
        email_id = request.GET.get('id', '')
    elif request.method == "POST":
        email_id = request.POST.get('id', '')
    else:
        return HttpResponse('错误请求')

    email_obj = get_object(Email_template, id=email_id)
    logger.debug(u"删除邮件模板 %s " % email_obj.name)
    email_obj.delete()
    return HttpResponse('删除成功')


@require_role('admin', 'role_admin')
def sys_email_detail(request):
    header_title, path1, path2 = "系统设置", "邮件模板管理", "邮件模板详情"
    email_id = request.GET.get('id', None)
    if not email_id:
        return HttpResponseRedirect(reverse(sys_email_list))
    email_obj = Email_template.objects.filter(id=email_id)
    if email_obj.count() == 1:
        file = None
        email_obj = email_obj[0]
        try:
            content = ''
            template_path = "%s%s%s" % (settings.BASE_DIR, "/templates/", email_obj.template_path)
            if os.path.exists(template_path):
                file = open(template_path)
                block = file.read(1024)
                while block:
                    content += block
                    block = file.read(1024)
            else:
                error = u"该邮件模板内容为空"
        except Exception, e:
            logger.error(u"邮件模板读取出错：%s" % e)
            error = u"邮件模板读取出错"
        finally:
            if file:
                file.close()
    elif email_obj.count() > 1:
        error = u"邮件模板不唯一"
    else:
        error = u"未找到邮件模板"
    return my_render('jperm/sys_email_detail.html', locals(), request)

@require_role('admin', 'role_admin')
def sys_email_save(request):
    email_id = request.GET.get('id', None)
    if not email_id:
        msg = u'未找到该邮件模板'
        return HttpResponse(msg)
    email_obj = Email_template.objects.filter(id=email_id)
    if email_obj.count() == 1:
        file = None
        email_obj = email_obj[0]
        try:
            content = request.GET.get('content', None)
            if content:
                template_path = "%s%s%s" % (settings.BASE_DIR, "/templates/", email_obj.template_path)
                file = open(template_path, 'wb+')
                file.write(content)
                msg = u"保存成功"
            else:
                msg = u"未传入模板邮件内容"
        except Exception, e:
            logger.error(u"邮件模板保存出错：%s" % e)
            msg = u"邮件模板保存出错"
        finally:
            if file:
                file.close()
    elif email_obj.count() > 1:
        msg = u"邮件模板不唯一"
    else:
        msg = u"未找到邮件模板"
    return HttpResponse(msg)


@require_role('admin', 'user_induction_list')
def sys_email_send(request):
    error = ''
    msg = ''
    header_title, path1, path2 = "系统设置", "邮件设置", "邮件发送"

    user_list = request.GET.get('id', '')
    user_id_list = user_list.split(',')
    emails_obj = Email_template.objects.all()
    users_obj = User.objects.all()

    if request.method == 'GET':
        func_name = request.GET.get('funcname', '')
        cc_email_dict = {}
        cc_selected = []

        if func_name == 'induction':
            users = []
            emails_obj = Email_template.objects.filter(id=3)
            emails_selected = [emails.id for emails in emails_obj[0].to_email.all()]

            for user_id in user_id_list:
                user_obj = get_object(User, id=user_id)
                users.append(user_obj)
                try:
                    user_guide = user_obj.guide
                    cc_email_dict[user_guide.username] = user_guide.id
                except Exception, e:
                    pass
                try:
                    user_parent = user_obj.parent
                    cc_email_dict[user_parent.username] = user_parent.id
                except Exception, e:
                    pass
                try:
                    user_group_admin = user_obj.group.dep_admin
                    cc_email_dict[user_group_admin.username] = user_group_admin.id
                except Exception, e:
                    pass

            for k in cc_email_dict:
                cc_selected.append(cc_email_dict[k])
        else:
            pass

    elif request.method == 'POST':
        email_template_id = request.POST.get("email_template", '')
        to_user_list = request.POST.getlist("user_list", '')
        cc_user_list = request.POST.getlist("cc_user_id", '')
        en_time = request.POST.get('entry_time', '')
        another_users = request.POST.get("another_users", '')
        sendname = User.objects.get(id=request.user.id)
        sendemail = request.user.username
        users = []
        to_email = []
        cc_email = []
        mail_obj = get_object(Email_template, id=email_template_id)

        if to_user_list:
            for send_to_uid in to_user_list:
                to_email.append(User.objects.get(id=send_to_uid).email)
        else:
            error = '收件人为空，请重新选择收件人！'
            return my_render('jperm/sys_email_send.html', locals(), request)

        if cc_user_list:
            for send_to_uid in cc_user_list:
                cc_email.append(User.objects.get(id=send_to_uid).email)

        if another_users:
            another_users_name = []
            another_users_list = another_users.split(",")
            for i in another_users_list:
                another_users_obj = get_object(User, id=i)
                another_users_name.append(another_users_obj.name)
            another_users_name = "、".join(another_users_name)
        else:
            another_users_name = ''
        for user_id in user_id_list:
            user_obj = get_object(User, id=user_id)
            users.append(user_obj)

        cc_email.append(sendname.email)
        email_value = {"users": users,
                       "en_time": en_time,
                       "another_users": another_users_name,
                       'sendname': sendname.name,
                       'sendemail': sendemail}
        try:
            send_emails(mail_obj, to_email, cc_email, email_value)
        except Exception, e:
            error = '邮件服务器返回异常：%s' % e
            return my_render('jperm/sys_email_send.html', locals(), request)
        msg = '邮件发送成功'
        return HttpResponseRedirect(reverse(user_induction_list))

    # return my_render('juser/group_edit.html', locals(), request)
    return my_render('jperm/sys_email_send.html', locals(), request)


# @require_role(role='admin')
# def post_email_send(request):
#     if request.method == "GET":
#         user_list = request.GET.get('id', '')
#         user_id_list = user_list.split(',')
#         to_email_dict = {}
#         to_email = []
#     else:
#         return HttpResponse('错误请求')
#     for user_id in user_id_list:
#         user_obj = get_object(User, id=user_id)
#         email_obj = get_object(Email_template, id=3)
#         user_guide = user_obj.guide
#         user_parent = user_obj.parent
#         user_group_admin = user_obj.group.dep_admin
#         try:
#             if user_guide:
#                 to_email_dict[user_guide.username] = user_guide.email
#             if user_parent:
#                 to_email_dict[user_parent.username] = user_parent.email
#             if user_group_admin:
#                 to_email_dict[user_group_admin.username] = user_group_admin.email
#         except Exception, e:
#             pass
#
#         for k in to_email_dict:
#             to_email.append(to_email_dict[k])
#         print "===",to_email
#
#     # send_email(mail_obj, to_email, msg)


# @require_role('user')
# def test_test(request):
#     menu_obj = menu.objects.filter(parent__isnull=True)
#     c_menu_obj = menu.objects.filter(parent__isnull=False)
#
#     role_id = int(request.user.role.id)
#     my_obj = menu_permission.objects.select_related(
#         'menu__url'
#     ).select_related('menu__name').filter(role_id=role_id)
#     m_list = [i.menu_id for i in my_obj]
#     print "m_list",m_list
#
#     data = []
#     for i in menu_obj:
#         dict_data = {}
#         c_data = []
#         i_menu_obj = c_menu_obj.filter(parent_id=i.id)
#         for j in i_menu_obj:
#             c_dict_data = {}
#             c_dict_data['id'] = j.id
#             c_dict_data['text'] = j.name
#             if j.id in m_list:
#                 print j.id,m_list
#                 c_dict_data['checked'] = True
#             else:
#                 print "no==",j.id, m_list
#                 c_dict_data['checked'] = False
#             c_data.append(c_dict_data)
#
#         dict_data['id'] = i.id
#         dict_data['text'] = i.name
#         dict_data['state'] = 'closed'
#         dict_data['children'] = c_data
#         # if i.id in m_list:
#         #     print i.id, m_list
#         #     dict_data['checked'] = True
#         # else:
#         #     dict_data['checked'] = False
#         data.append(dict_data)
#
#     data = json.dumps(data)
#
#     if request.method == 'POST':
#         role_id_list = request.POST.getlist('role_id_list', [])
#         print "role_id_list=", role_id_list
#         return my_render('jperm/test_1.html', locals(), request)
#
#     return my_render('jperm/test_1.html', locals(), request)


@require_role('admin', 'role_admin')
def get_menu_dict(request):
    role_id = request.GET.get('id', '')

    menu_obj = menu.objects.filter(parent__isnull=True)
    c_menu_obj = menu.objects.filter(parent__isnull=False)

    print "role_id=", role_id
    if role_id:
        my_obj = menu_permission.objects.select_related(
            'menu__url'
        ).select_related('menu__name').filter(role_id=role_id)
        m_list = [i.menu_id for i in my_obj]
    else:
        m_list = []

    data = []
    for i in menu_obj:
        dict_data = {}
        c_data = []
        i_menu_obj = c_menu_obj.filter(parent_id=i.id)
        for j in i_menu_obj:
            c_dict_data = {}
            c_dict_data['id'] = j.id
            c_dict_data['text'] = j.name
            if j.id in m_list:
                c_dict_data['checked'] = True
            else:
                c_dict_data['checked'] = False
            c_data.append(c_dict_data)

        dict_data['id'] = i.id
        dict_data['text'] = i.name
        dict_data['state'] = 'closed'
        dict_data['children'] = c_data
        data.append(dict_data)
    return JsonResponse(data, safe=False)


@require_role('admin', 'role_admin')
def user_passwd_list(request):
    header_title, path1, path2 = "用户列表", "系统管理", "用户变更"

    user_list = User.objects.all()
    keyword = request.GET.get('search', '')
    if keyword:
        user_list = user_list.filter(Q(name=keyword)|Q(username__icontains=keyword))

    roles_list, p, user_list, page_range, current_page, show_first, show_end = pages(user_list, request)

    return my_render('jperm/perm_user_list.html', locals(), request)


@require_role('admin', 'role_admin')
def passwd_update(request):
    header_title, path1, path2 = "系统设置", "用户密码管理", "密码变更"
    try:
        user_id = request.GET.get('id', '')
        user_obj = get_object(User, id=user_id)
        if user_obj is None:
            error = u'用户不存在！'
            return my_render('jperm/passwd_update.html', locals(), request)

        if request.method == 'POST':
            first_passwd = request.POST.get('first_passwd', '')
            second_passwd = request.POST.get('second_passwd', '')

            if (not first_passwd) or (not second_passwd):
                error = u'密码不能为空！'
                return my_render('jperm/passwd_update.html', locals(), request)

            if first_passwd == second_passwd:
                user_obj.set_password(first_passwd)
                user_obj.save()
                msg = u'密码重置成功'
            else:
                error = u'两次输入不一致，请重新输入！'
        return my_render('jperm/passwd_update.html', locals(), request)
    except Exception, e:
        error = u'密码重置异常：%s' % e
        logger.error(error)
        return my_render('jperm/passwd_update.html', locals(), request)


@require_role('user')
def passwd_update_self(request):
    header_title, path1, path2 = "系统设置", "用户密码管理", "密码变更"
    try:
        user_obj = get_object(User, id=request.user.id)

        if request.method == 'POST':
            first_passwd = request.POST.get('first_passwd', '')
            second_passwd = request.POST.get('second_passwd', '')

            if (not first_passwd) or (not second_passwd):
                error = u'密码不能为空！'
                return my_render('jperm/passwd_update.html', locals(), request)

            if first_passwd == second_passwd:
                user_obj.set_password(first_passwd)
                user_obj.save()
                msg = u'密码重置成功'
            else:
                error = u'两次输入不一致，请重新输入！'
        return my_render('jperm/passwd_update.html', locals(), request)
    except Exception, e:
        error = u'个人密码重置异常：%s' % e
        logger.error(error)
        return my_render('jperm/passwd_update.html', locals(), request)