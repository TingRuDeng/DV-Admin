# coding: utf-8

import re
from django.shortcuts import get_object_or_404
from django.db.models import Q
from juser.user_api import *
from jperm.perm_api import *
from jlog.models import ManagerLog

MAIL_FROM = EMAIL_HOST_USER


@require_role('admin', 'user_group_list')
def group_add(request):
    """
    group add view for route
    添加部门
    """
    error = ''
    msg = ''
    header_title, path1, path2 = '部门添加', '部门管理', '部门添加'
    user_all = User.objects.filter(is_active=1)
    group_all = UserGroup.objects.filter(is_active=1)

    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        # users_selected = request.POST.getlist('users_selected', '')
        dep_parent = request.POST.get('parent_id', '')
        dep_admin = request.POST.get('dep_admin', '')
        comment = request.POST.get('comment', '')

        try:
            if not group_name:
                error = u'部门名称 不能为空'
                raise ServerError(error)

            if UserGroup.objects.filter(name=group_name):
                error = u'部门已存在'
                raise ServerError(error)
            user_id = request.user.id
            db_add_group(name=group_name, user_id=user_id, parent=dep_parent, dep_admin=dep_admin, comment=comment)
        except ServerError:
            pass
        except TypeError:
            error = u'添加部门失败'
        else:
            msg = u'添加部门 %s 成功' % group_name
            return HttpResponseRedirect(reverse('user_group_list'))
    return my_render('juser/group_add.html', locals(), request)


@require_role('admin', 'user_group_list')
def group_list(request):
    """
    list user group
    用户组列表
    """
    header_title, path1, path2 = '部门查看', '部门管理', '员工查看'
    keyword = request.GET.get('search', '')
    user_group_list = UserGroup.objects.filter(is_active=1).order_by('name')
    group_id = request.GET.get('id', '')

    if keyword:
        user_group_list = user_group_list.filter(Q(name__icontains=keyword) | Q(comment__icontains=keyword) |
                                                 Q(parent__name__icontains=keyword))

    if group_id:
        user_group_list = user_group_list.filter(id=int(group_id))

    user_group_list, p, user_groups, page_range, current_page, show_first, show_end = pages(user_group_list, request)
    return my_render('juser/group_list.html', locals(), request)


@require_role('admin', 'user_group_list')
def group_del(request):
    """
    del a group
    删除用户组
    """
    if request.method == "GET":
        group_ids = request.GET.get('id', '')
        group_id_list = group_ids.split(',')
    elif request.method == "POST":
        group_ids = request.POST.get('id', '')
        group_id_list = group_ids.split(',')
    else:
        return HttpResponse('错误请求')

    for group_id in group_id_list:
        group = get_object(UserGroup, id=group_id)
        if User.objects.filter(group_id=group_id, is_active=1, is_staff=1).count() != 0:
            error = 'error 0'
            try:
                error = u'部门（%s）下员工不为空，不允许删除！' % group.name
                raise ServerError
            except ServerError:
                return HttpResponse(error)
        else:
            try:
                logger.debug(u"删除部门 %s " % group.name)
                dep_obj = UserGroup.objects.filter(id=group_id)
                dep_obj.update(is_active=0)
                ManagerLog.objects.create(user_id=request.user.id, type='部门删除', msg=model_to_dict(dep_obj[0]))
            except Exception as e:
                logger.error("日志记录异常！%s" % e)
    return HttpResponse('删除成功')


@require_role('admin', 'user_group_list')
def group_edit(request):
    error = ''
    msg = ''
    header_title, path1, path2 = '部门变更', '部门管理', '部门信息变更'

    group_id = request.GET.get('id', '')
    user_group = get_object(UserGroup, id=group_id)
    users_list = User.objects.filter(group=user_group, is_active=1, is_staff=1)
    users_selected = [i.id for i in users_list]

    if request.method == 'GET':
        users_remain = User.objects.exclude(id=1).filter(is_active=1, is_staff=1)
        if user_group.dep_admin:
            users_all = User.objects.exclude(id=1).exclude(id=user_group.dep_admin.id).filter(is_active=1, is_staff=1)
        else:
            users_all = User.objects.exclude(id=1).filter(is_active=1, is_staff=1)
        if user_group.parent:
            group_all = UserGroup.objects.exclude(id=user_group.parent.id, is_active=0).exclude(id=group_id)
        else:
            group_all = UserGroup.objects.filter(is_active=1).exclude(id=group_id)

    elif request.method == 'POST':
        group_id = request.POST.get('group_id', '')
        group_name = request.POST.get('group_name', '')
        group_parent = request.POST.get('parent_id', '')
        group_dep_admin = request.POST.get('dep_admin', '')
        comment = request.POST.get('comment', '')
        users_post = request.POST.getlist('users_add_list', [])
        try:
            if '' in [group_id, group_name]:
                raise ServerError('部门不能为空')

            if len(UserGroup.objects.filter(name=group_name)) > 1:
                raise ServerError(u'%s 部门已存在' % group_name)
            # add user group

            add_menu = diff_list(users_post, users_selected)
            del_menu = diff_list(users_selected, users_post)

            user_group = get_object_or_404(UserGroup, id=group_id)
            # user_group.group_id.clear()

            if add_menu:
                for user in User.objects.filter(id__in=add_menu):
                    ManagerLog.objects.create(user_id=request.user.id,
                                              type=u'部门信息变更-员工部门变更前',
                                              msg=model_to_dict(user))
                    user.group = UserGroup.objects.get(id=group_id)
                    user.save()
                    ManagerLog.objects.create(user_id=request.user.id,
                                              type=u'部门信息变更-员工部门变更后',
                                              msg=model_to_dict(user))
            if del_menu:
                for i in del_menu:
                    user_obj = User.objects.filter(id=i)
                    ManagerLog.objects.create(user_id=request.user.id,
                                              type=u'部门信息变更-员工部门变更前',
                                              msg=model_to_dict(user_obj[0]))
                    user_obj.update(group='')
                    ManagerLog.objects.create(user_id=request.user.id,
                                              type=u'部门信息变更-员工部门变更后',
                                              msg=model_to_dict(user_obj[0]))

            ManagerLog.objects.create(user_id=request.user.id,
                                      type=u'部门信息变更前',
                                      msg=model_to_dict(user_group))
            user_group.name = group_name

            if group_parent:
                group_parent_obj = UserGroup.objects.get(id=group_parent)
                user_group.parent = group_parent_obj
            if group_dep_admin:
                dep_admin_obj = User.objects.get(id=group_dep_admin)
                user_group.dep_admin = dep_admin_obj

            user_group.comment = comment
            user_group.save()
            ManagerLog.objects.create(user_id=request.user.id, type='部门信息变更后', msg=model_to_dict(user_group))
        except ServerError as e:
            logger.error(u'部门变更失败：%s' % e)
            error = e

        if not error:
            return HttpResponseRedirect(reverse('user_group_list'))
        else:
            users_all = User.objects.filter(is_active=1, is_staff=1)
            users_selected = User.objects.filter(group=user_group, is_active=1, is_staff=1)
            users_remain = User.objects.filter(~Q(group=user_group), is_active=1, is_staff=1)

    return my_render('juser/group_edit.html', locals(), request)


@require_role('admin', 'user_list')
def user_add(request):
    error = ''
    msg = ''
    header_title, path1, path2 = '员工添加', '员工管理', '员工添加'

    group_all = UserGroup.objects.filter(is_active=1)
    user_all = User.objects.filter(is_active=1)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        first_name = first_name.strip()
        last_name = request.POST.get('last_name', '')
        last_name = last_name.strip()
        username = request.POST.get('username', '')
        name = first_name + last_name
        groups = request.POST.get('groups', '')
        uuid_r = uuid.uuid4().get_hex()
        sex = request.POST.get('sex', '')
        mobile = request.POST.get('mobile', '')
        wechat = request.POST.get('wechat', '')
        job = request.POST.get('job', '')
        parent_id = request.POST.get('parent', '')
        is_active = True

        try:
            if '' in [username, name]:
                error = u'带*内容不能为空'
                raise ServerError
                
            check_user_is_exist = User.objects.filter(username=username)
            if check_user_is_exist:
                error = u'账户 %s 已存在' % username
                raise ServerError

            check_name_is_exist = User.objects.filter(name=name)
            if check_name_is_exist:
                error = u'%s 已有同名存在，请增加后缀进行区分' % name
                raise ServerError

            if username in ['root']:
                error = u'用户不能为root'
                raise ServerError

        except ServerError:
            pass
        else:
            try:
                if not re.match(r"^\w+$", username):
                    error = u'账户不合法'
                    raise ServerError(error)
                user = db_add_user(username=username, name=name, first_name=first_name, last_name=last_name,
                                   role=1, uuid=uuid_r, groups=groups, sex=sex, mobile=mobile, wechat=wechat,
                                   parent=parent_id, job=job, is_active=is_active, is_staff=True,
                                   date_joined=datetime.datetime.now())

                return HttpResponseRedirect(reverse('user_list'))

            except IndexError as e:
                error = u'添加用户 %s 失败 %s ' % (username, e)
                logger.error(error)
                try:
                    db_del_user(username)
                except Exception as e:
                    logger.warning(u'删除新增失败的用户异常：%s' % e)
    return my_render('juser/user_add.html', locals(), request)


# @require_role('admin', 'user_induction_list')
# def user_add_batch(request):
#     # 批量添加员工数据
#     return my_render('juser/user_add_batch.html', locals(), request)


# @require_role('admin', 'user_induction_list')
# def user_upload(request):
#     header_title, path1, path2 = '员工批量添加', '员工管理', '员工批量添加'
#
#     if request.method == 'POST':
#         user_id = request.user.id
#         excel_file = request.FILES.get('file_name', '')
#         ret, dic_len = excel_user_to_db(excel_file, user_id, request)
#         if ret is True:
#             smg = u'成功添加 %s 条' %dic_len
#             return my_render('juser/user_add_batch.html', locals(), request)
#         elif ret is False:
#             emg = u'导入失败，请确认导入的Excel文件是否有效.'
#             return my_render('juser/user_add_batch.html', locals(), request)
#         else:
#             error_list = ret
#             return my_render('juser/user_add_error.html', locals(), request)
#     else:
#         pass


# @require_role('admin', 'user_induction_list')
# def userprivate_upload(request):
#     """
#     批量上传员工自有信息
#     :param request:
#     :return:
#     """
#     if request.method == 'POST':
#         ret = False
#         dic_len = 0
#         birthday_file = request.FILES.get('birthday', '')
#         workday_file = request.FILES.get('workday', '')
#         if birthday_file:
#             ret, dic_len = excel_birthday_to_db(birthday_file, request)
#         elif workday_file:
#             ret, dic_len = excel_workday_to_db(workday_file, request)
#         else:
#             pass
#         if ret is True:
#             smg = u'成功添加 %s 条' % dic_len
#             return HttpResponse(smg)
#         else:
#             logger.warning(u'导入失败')
#             return JsonResponse(ret, safe=False)
#     else:
#         return HttpResponse(u'请求错误')


# @require_role('admin', 'user_induction_list')
# def get_working_age(request):
#     if request.method == 'POST':
#         try:
#             from jattendance.models import leave_record
#             from django.db.models import Sum
#
#             now_time = request.POST.get('now_time', '')
#             if now_time is None:
#                 now_time = datetime.datetime.now()
#             else:
#                 now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d')
#             users_obj = User.objects.filter(is_staff=True, is_active=True, userprivate__isnull=False)
#             with open('/opt/Assets/static/files/excels/work_age.csv', 'wb') as csv_file:
#                 csv_file.write(codecs.BOM_UTF8)
#                 spam_writer = csv.writer(csv_file, dialect='excel')
#                 spam_writer.writerow([u'员工工号', u'姓名', u'至今应有年假', u'已用年假', u'剩余年假'])
#                 for users in users_obj:
#                     annual_fixed = users.holiday_fix
#                     annual_used = leave_record.objects.filter(user=users,
#                                                               reason_id=1
#                                                               ).aggregate(Sum('number'))['number__sum']
#                     if annual_fixed is None:
#                         annual_fixed = 0
#                     if annual_used is None:
#                         annual_used = 0
#                     annual_used = float(annual_used + annual_fixed) / 2
#
#                     if users.userprivate.first_work_day is None or users.entry_time is None:
#                         spam_writer.writerow([
#                             users.code,
#                             users.name,
#                             u"无记录",
#                             annual_used,
#                             u"无记录",
#                         ])
#                         continue
#                     # working_age = cal_user_holiday(users,
#                     #                                users.entry_time,
#                     #                                now_time)
#
#                     spam_writer.writerow([
#                         users.code,
#                         users.name,
#                         working_age,
#                         annual_used,
#                         working_age - float(annual_used)
#                     ])
#             return HttpResponse(u'导入成功')
#         except Exception, e:
#             print "===%s" % e
#             return HttpResponse(u'导入失败:%s' % e)
#     else:
#         return HttpResponse(u'请求错误')


@require_role('admin', 'user_list')
def user_edit(request):
    header_title, path1, path2 = '员工编辑', '员工管理', '员工编辑'

    user_id = request.GET.get('id', '')
    if not user_id:
        return HttpResponseRedirect(reverse('index'))

    user = get_object(User, id=user_id)
    group_obj = user.group
    user_all = User.objects.exclude(id__in=[1, user_id])

    if group_obj:
        group_all = UserGroup.objects.filter(is_active=1).exclude(id=group_obj.id)
    else:
        group_all = UserGroup.objects.filter(is_active=1)

    if request.method == 'POST':
        # code = request.POST.get('code', '')
        name = request.POST.get('name', '')
        # email = request.POST.get('email', '')
        groups = request.POST.get('groups', '')
        sex = request.POST.get('sex', '')
        mobile = request.POST.get('mobile', '')
        wechat = request.POST.get('wechat', '')
        # birthday = request.POST.get('birthday', '')
        # first_work_day = request.POST.get('first_work_day', '')

        job = request.POST.get('job', '')
        parent_id = request.POST.get('parent', '')
        # guide_id = request.POST.get('guide', '')
        # empway_id = request.POST.get('empway', '')
        # position_id = request.POST.get('position', '')
        # entry_time = request.POST.get('entry_time', '')
        # extra = request.POST.getlist('extra', [])
        # email_need = True if '1' in extra else False

        ManagerLog.objects.create(user_id=request.user.id,
                                  type=u'员工信息变更前',
                                  msg=model_to_dict(User.objects.get(id=user_id)))
        user_update = db_update_user(user_id=user_id, name=name, groups=groups, sex=sex, mobile=mobile,
                                     wechat=wechat, parent=parent_id, job=job)
        ManagerLog.objects.create(user_id=request.user.id,
                                  type='员工信息变更后',
                                  msg=model_to_dict(user_update))
        return HttpResponseRedirect(reverse('user_list'))
    return my_render('juser/user_edit.html', locals(), request)


# def get_user_pic(request):
#     try:
#         if request.method == 'POST':
#             fid = request.POST.get('fid', '')
#             user_obj = User.objects.filter(is_active=True, is_staff=True, portrait_address__isnull=False)
#             result = []
#             for user in user_obj:
#                 if (user.id % 3) == int(fid):
#                     result.append({"name": user.name,
#                                    "pic_no":  str(user.portrait_address).split('/')[-1]})
#             result = json.dumps(result)
#             response = HttpResponse(result)
#             response["Access-Control-Allow-Origin"] = "*"
#             # return JsonResponse(result, safe=False)
#             return response
#         else:
#             return HttpResponse('非法请求，如有疑问请联系管理员！')
#     except Exception, e:
#         logger.error(u'get_user_pic获取异常: %s' % e)


# @require_role('admin', 'user_induction_list')
# def user_induction_list(request):
#     header_title, path1, path2 = '入职员工查看', '员工管理', '入职员工列表'
#
#     # active_status = {'0': u'预入职', '2': u'离职'}
#     # users_in = User.objects.filter(is_active=1, is_staff=0).order_by('entry_time')
#     # users_out = User.objects.filter(is_active=0).order_by('departure_time')
#     users_list = User.objects.filter(is_active=1, is_staff=0).order_by('entry_time', 'departure_time')
#     email_user_list = User.objects.filter(is_active=1, is_staff=1)
#     # position_obj = userposition.objects.all()
#     group_obj = UserGroup.objects.filter(is_active=1)
#
#     keyword = request.GET.get('keyword')
#     user_group = request.GET.get('user_group')
#     # user_active = request.GET.get('user_active')
#     user_position = request.GET.get('user_position')
#     user_sex = request.GET.get('user_sex')
#     # gid = request.GET.get('gid')
#
#     # 界面模糊搜索匹配并返回结果
#     if keyword:
#         users_list = users_list.filter(Q(username__icontains=keyword) |
#         Q(name__icontains=keyword)).order_by('username')
#
#     # if user_active == '1':
#     #     users_list = users_list.filter(is_active=1)
#     # elif user_active == '0':
#     #     users_list = users_list.filter(is_active=0)
#     if user_position:
#         users_list = users_list.filter(position=int(user_position))
#     if user_sex:
#         users_list = users_list.filter(sex=user_sex)
#     if user_group:
#         users_list = users_list.filter(group=int(user_group))
#
#     # if gid:
#     #     dep_list = []
#     #     deps = UserGroup.objects.filter(parent_id=gid)
#     #     if deps:
#     #         dep_list = [i.id for i in deps]
#     #     dep_list.append(gid)
#     #     users_list = users_list.filter(group_id__in=dep_list)
#
#     # 分页，界面从users取当前页内容
#     users_list, p, users, page_range, current_page, show_first, show_end = pages(users_list, request)
#
#     return my_render('juser/user_induction_list.html', locals(), request)


# @require_role('admin')
# def induction_email(request):
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
#     send_email(mail_obj, to_email, msg)


# @require_role('admin', 'user_induction_list')
# def user_induction(request):
#
#     header_title, path1, path2 = '入职确认', '员工管理', '入职确认'
#
#     user_id = request.GET.get('id', '')
#     username = request.POST.get('username', '')
#     if not user_id:
#         return HttpResponseRedirect(reverse('index'))
#
#     user = get_object(User, id=user_id)
#     if user.is_staff == 1:
#         try:
#             error = u'该员工已走完入职流程'
#             raise ServerError
#         except ServerError:
#             return HttpResponseRedirect(reverse('user_list'))
#
#     if request.method == 'POST':
#         code_id = request.POST.get('code', '')
#         en_time = request.POST.get('entry_time', '')
#
#         try:
#             check_code_is_exist = User.objects.exclude(id=user_id).filter(code=code_id)
#             if check_code_is_exist:
#                 error = u'工号 %s 已存在' % code_id
#                 raise ServerError
#             else:
#                 user.code = code_id
#                 user.entry_time = en_time
#                 user.is_staff = True
#                 user.save()
#                 # unblock_ldap_user(username)
#
#                 ManagerLog.objects.create(user_id=request.user.id, type='待入职员工入职',
#                                           msg=model_to_dict(user))
#                 return HttpResponseRedirect(reverse('user_induction_list'))
#         except ServerError:
#             pass
#
#     return my_render('juser/user_induction.html', locals(), request)


# @require_role('admin')
# def user_positive(request):
#     header_title, path1, path2 = '待转正员工查看', '待转正员工管理', '待转正员工列表'
#
#     users_list = User.objects.filter(is_active=1, is_staff=1, positive_time=None).exclude(id=1).order_by('entry_time')
#     # position_obj = userposition.objects.all()
#     group_obj = UserGroup.objects.filter(is_active=1)
#
#     keyword = request.GET.get('keyword')
#     user_group = request.GET.get('user_group')
#     # user_active = request.GET.get('user_active')
#     user_position = request.GET.get('user_position')
#     user_sex = request.GET.get('user_sex')
#     gid = request.GET.get('gid')
#
#     # 界面模糊搜索匹配并返回结果
#     if keyword:
#         users_list = users_list.filter(Q(username__icontains=keyword) |
#                                        Q(name__icontains=keyword) |
#                                        Q(parent__name__icontains=keyword) |
#                                        Q(code__icontains=keyword)).order_by('username')
#
#     # if user_active:
#     #     users_list = users_list.filter(is_active=int(user_active))
#     if user_position:
#         users_list = users_list.filter(position=int(user_position))
#     if user_sex:
#         users_list = users_list.filter(sex=user_sex)
#     if user_group:
#         users_list = users_list.filter(group=int(user_group))
#
#     if gid:
#         dep_list = []
#         deps = UserGroup.objects.filter(parent_id=gid)
#         if deps:
#             dep_list = [i.id for i in deps]
#         dep_list.append(gid)
#         users_list = users_list.filter(group_id__in=dep_list)
#
#     # 分页，界面从users取当前页内容
#     users_list, p, users, page_range, current_page, show_first, show_end = pages(users_list, request)
#
#     return my_render('juser/positive_list.html', locals(), request)


# @require_role('admin', 'user_departure_list')
# def user_departure_list(request):
#     header_title, path1, path2 = '离职员工查看', '员工管理', '离职员工列表'
#
#     users_list = User.objects.filter(is_active=0, is_staff=1).order_by('-departure_time', 'entry_time')
#     # position_obj = userposition.objects.all()
#     group_obj = UserGroup.objects.all()
#
#     keyword = request.GET.get('keyword')
#     user_group = request.GET.get('user_group')
#     user_position = request.GET.get('user_position')
#     user_sex = request.GET.get('user_sex')
#
#     # 界面模糊搜索匹配并返回结果
#     if keyword:
#         users_list = users_list.filter(Q(username__icontains=keyword) |
#         Q(name__icontains=keyword)).order_by('username')
#
#     if user_position:
#         users_list = users_list.filter(position=int(user_position))
#     if user_sex:
#         users_list = users_list.filter(sex=user_sex)
#     if user_group:
#         users_list = users_list.filter(group=int(user_group))
#
#     # 分页，界面从users取当前页内容
#     users_list, p, users, page_range, current_page, show_first, show_end = pages(users_list, request)
#
#     return my_render('juser/user_departure_list.html', locals(), request)


@require_role('admin', 'user_list')
def user_departure(request):
    header_title, path1, path2 = '账号注销确认', '员工账号管理', '注销注销确认'

    user_id = request.GET.get('id', '')
    username = request.POST.get('username', '')

    if not user_id:
        return HttpResponseRedirect(reverse('index'))

    user = get_object(User, id=user_id)
    parent_list = User.objects.filter(parent_id=user_id)
    dep_list = UserGroup.objects.filter(dep_admin_id=user_id)

    if request.method == 'POST':
        # code_id = request.POST.get('code', '')
        dep_time = datetime.datetime.now()

        # if asset_count != 0:
        #     try:
        #         error = u'该员工名下还有资产未归还，无法办理离职手续'
        #         raise ServerError
        #     except ServerError:
        #         return my_render('juser/user_departure.html', locals(), request)

        user.departure_time = dep_time
        user.is_active = False
        user.username = str(time.time())
        user.role_id = 1
        user.save()
        ManagerLog.objects.create(user_id=request.user.id,
                                  type='员工账号注销确认',
                                  msg=model_to_dict(user))
        User.objects.filter(parent_id=user_id).update(parent_id=None)
        UserGroup.objects.filter(dep_admin_id=user_id).update(dep_admin_id=None)
        # remove_member_to_lock_group(username)
        return HttpResponseRedirect(reverse('user_list'))

    return my_render('juser/user_departure.html', locals(), request)


# @require_role('admin', 'user_induction_list')
# def user_termination(request):
#
#     """
#     入职流程终止，对应username置为当前时间戳字符串
#     :param request:
#     :return:
#     """
#
#     if request.method == "GET":
#         user_id = request.GET.get('id', '')
#     elif request.method == "POST":
#         user_id = request.GET.get('id', '')
#     else:
#         return HttpResponse('错误请求')
#     try:
#         user = get_object(User, id=user_id)
#         user.username = str(time.time())
#         user.is_active = False
#         user.save()
#         ManagerLog.objects.create(user_id=request.user.id, type='入职流程终止',
#                                   msg=model_to_dict(user))
#         return HttpResponseRedirect(reverse('user_induction_list'))
#     except ServerError:
#         pass
#
#     return my_render('juser/user_induction.html', locals(), request)


@require_role('admin', 'user_list')
def user_list(request):
    header_title, path1, path2 = '员工查看', '员工管理', '员工列表'

    users_list = User.objects.filter(is_active=1)
    # position_obj = userposition.objects.all()
    group_obj = UserGroup.objects.filter(is_active=1)

    keyword = request.GET.get('keyword')
    user_group = request.GET.get('user_group')
    # user_active = request.GET.get('user_active')
    # user_position = request.GET.get('user_position')
    user_sex = request.GET.get('user_sex')
    gid = request.GET.get('gid')

    # 界面模糊搜索匹配并返回结果
    if keyword:
        users_list = users_list.filter(Q(username__icontains=keyword) |
                                       Q(name__icontains=keyword) |
                                       Q(parent__name__icontains=keyword)
                                       ).order_by('username')

    if user_sex:
        users_list = users_list.filter(sex=user_sex)
    if user_group:
        users_list = users_list.filter(group=int(user_group))

    if gid:
        dep_list = []
        deps = UserGroup.objects.filter(parent_id=gid)
        if deps:
            dep_list = [i.id for i in deps]
        dep_list.append(gid)
        users_list = users_list.filter(group_id__in=dep_list)

    # 分页，界面从users取当前页内容
    users_list, p, users, page_range, current_page, show_first, show_end = pages(users_list, request)

    return my_render('juser/user_list.html', locals(), request)


@require_role('user')
def user_detail(request):
    header_title, path1, path2 = '员工信息', '组织管理', '个人信息详情'

    user_id = request.GET.get('id')
    if user_id:
        user_obj = get_user_data(request, id=user_id)
    else:
        user_obj = get_user_data(request, id=request.user.id)

    try:
        user_obj = user_obj[0]
    except Exception as e:
        logger.warning(u'获取员工列表失败: %s' % e)

    if not user_obj:
        return HttpResponseRedirect(reverse('user_list'))

    user_log_ten = Log.objects.filter(user=user_obj.username).order_by('id')[0:10]
    user_log_last = Log.objects.filter(user=user_obj.username).order_by('id')[0:50]
    user_log_last_num = len(user_log_last)
    # user_consumables = get_user_consumables(user_obj)
    # user_consumables_sum = 0
    # for consumable in user_consumables:
    #     user_consumables_sum += consumable["user_quantity"]
    return my_render('juser/user_detail.html', locals(), request)


# @require_role('admin','user_list')
# def user_del(request):
#     if request.method == "GET":
#         user_ids = request.GET.get('id', '')
#         user_id_list = user_ids.split(',')
#     elif request.method == "POST":
#         user_ids = request.POST.get('id', '')
#         user_id_list = user_ids.split(',')
#     else:
#         return HttpResponse('错误请求')
#
#     for user_id in user_id_list:
#         user = get_object(User, id=user_id)
#         user_admin_group = UserGroup.objects.filter(dep_admin=user_id)
#         if user_admin_group:
#             try:
#                 error = u'该员工为部门负责人，请在部门管理中移除后再进行删除'
#                 raise ServerError
#             except ServerError:
#                 return HttpResponse(error)
#         if user and user.username != 'admin':
#             logger.debug(u"删除用户 %s " % user.username)
#             # server_del_user(user.username)
#             user.delete()
#     return HttpResponse('删除成功')


# @require_role('admin')
# def send_mail_retry(request):
#     uuid_r = request.GET.get('uuid', '1')
#     user = get_object(User, uuid=uuid_r)
#     msg = u"""
#     跳板机地址： %s
#     用户名：%s
#     重设密码：%s/juser/password/forget/
#     请登录web点击个人信息页面重新生成ssh密钥
#     """ % (URL, user.username, URL)
#
#     try:
#         send_mail(u'邮件重发', msg, MAIL_FROM, [user.email], fail_silently=False)
#     except IndexError:
#         return Http404
#     return HttpResponse('发送成功')


# @defend_attack
# def forget_password(request):
#     if request.method == 'POST':
#         defend_attack(request)
#         email = request.POST.get('email', '')
#         username = request.POST.get('username', '')
#         name = request.POST.get('name', '')
#         user = get_object(User, username=username, email=email, name=name)
#         if user:
#             timestamp = int(time.time())
#             hash_encode = PyCrypt.md5_crypt(str(user.uuid) + str(timestamp) + KEY)
#             msg = u"""
#             Hi %s, 请点击下面链接重设密码！
#             %s/juser/password/reset/?uuid=%s&timestamp=%s&hash=%s
#             """ % (user.name, URL, user.uuid, timestamp, hash_encode)
#             send_mail('忘记跳板机密码', msg, MAIL_FROM, [email], fail_silently=False)
#             msg = u'请登陆邮箱，点击邮件重设密码'
#             return http_success(request, msg)
#         else:
#             error = u'用户不存在或邮件地址错误'
#
#     return render_to_response('juser/forget_password.html', locals())


# @defend_attack
# def reset_password(request):
#     uuid_r = request.GET.get('uuid', '')
#     timestamp = request.GET.get('timestamp', '')
#     hash_encode = request.GET.get('hash', '')
#     action = '/juser/password/reset/?uuid=%s&timestamp=%s&hash=%s' % (uuid_r, timestamp, hash_encode)
#
#     if hash_encode == PyCrypt.md5_crypt(uuid_r + timestamp + KEY):
#         if int(time.time()) - int(timestamp) > 600:
#             return http_error(request, u'链接已超时')
#     else:
#         return HttpResponse('hash校验失败')
#
#     if request.method == 'POST':
#         password = request.POST.get('password')
#         password_confirm = request.POST.get('password_confirm')
#         print password, password_confirm
#         if password != password_confirm:
#             return HttpResponse('密码不匹配')
#         else:
#             user = get_object(User, uuid=uuid_r)
#             if user:
#                 user.set_password(password)
#                 user.save()
#                 return http_success(request, u'密码重设成功')
#             else:
#                 return HttpResponse('用户不存在')
#
#     else:
#         return render_to_response('juser/reset_password.html', locals())
#
#     return http_error(request, u'错误请求')


@require_role('user')
def profile(request):
    user_id = request.user.id
    if not user_id:
        return HttpResponseRedirect(reverse('index'))
    user = User.objects.get(id=user_id)
    return my_render('juser/profile.html', locals(), request)


def change_info(request):
    header_title, path1, path2 = '修改信息', '员工管理', '修改员工信息'
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    error = ''
    if not user:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        name = request.POST.get('name', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')

        if '' in [name, email]:
            error = '不能为空'

        if not error:
            user.name = name
            user.email = email
            user.save()
            if len(password) > 0:
                user.set_password(password)
                user.save()
            msg = '修改成功'

    return my_render('juser/change_info.html', locals(), request)


@require_role('admin', 'portrait_list')
def portrait_list(request):
    header_title, path1, path2 = '上传员工头像', '员工管理', '修改员工头像'
    users = User.objects.exclude(id=1)

    keyword = request.GET.get('keyword', '')
    user_group = request.GET.get('user_group', '')
    user_position = request.GET.get('user_position', '')
    user_sex = request.GET.get('user_sex', '')
    emp_way = request.GET.get('emp_way')
    status = request.GET.get('status')
    if emp_way:
        emp_way = int(emp_way)
    if status:
        status = int(status)
    group_obj = UserGroup.objects.filter(is_active=True)

    if keyword:
        users = users.filter(Q(username__icontains=keyword) | Q(name__icontains=keyword))
    if user_group:
        users = users.filter(group_id=int(user_group))
    if user_position:
        users = users.filter(position=int(user_position))
    if user_sex:
        users = users.filter(sex=user_sex)
    if emp_way == 0:
        users = users.filter(is_active=1, is_staff=1)
        emp_way = u'在职'
    elif emp_way == 1:
        users = users.filter(is_active=0).order_by('-departure_time', 'entry_time')
        emp_way = u'离职'

    if status == 0:
        users = users.filter(portrait_address__isnull=False)
        status = u'已上传'
    elif status == 1:
        users = users.filter(portrait_address__isnull=True)
        status = u'未上传'

    user_list_all, p, users_list, page_range, current_page, show_first, show_end = pages(users, request)
    return my_render('juser/portrait_list.html', locals(), request)


@require_role('admin', 'portrait_list')
def portrait_upload(request):
    header_title, path1, path2 = '上传员工头像', '员工管理', '修改员工头像'
    user_id = request.GET.get('id')
    user = get_object(User, id=user_id)
    if user is None:
        return HttpResponseRedirect(reverse('portrait_list'))
    if request.method == 'POST':
        try:
            image = request.FILES.get("portrait", None)
            if image is None:
                return HttpResponseRedirect(reverse('portrait_list'))
            else:
                img_size = image.size
                img_url = image.name
                pattern = re.compile(r'(gif|jpg|jpeg|GIF|JPG|JPEG|png)$')
                match = pattern.match(img_url.split('.')[-1])
                if not match:
                    emg = u'请上传gif|jpg|jpeg|GIF|JPG|JPEG|png为后缀的图片'
                    return my_render('juser/portrait_admin_upload.html', locals(), request)
                if img_size > FILE_UPLOAD_MAX_SIZE:
                    emg = u'图片大小不能超过%fM' % round(FILE_UPLOAD_MAX_SIZE / 1024.0 / 1024.0, 4)
                    return my_render('juser/portrait_admin_upload.html', locals(), request)

                img_url_list = str(image.name).split('.')
                img_storage_name = "%s_%d.%s" % (str(uuid.uuid4().get_hex().lower()[0:8]), user.id, img_url_list[-1])
                image_dir = "%s%s%s" % (BASE_DIR, IMAGE_URL, "portrait")
                if not os.path.exists(image_dir):
                    os.mkdir(image_dir, 755)
                img_storage_path = os.path.join(image_dir, img_storage_name)

                with open(img_storage_path, 'wb+') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
                    f.close()
                if user.portrait_address:
                    ManagerLog.objects.create(user_id=request.user.id, type='头像-修改前', msg=model_to_dict(user))
                    user.portrait_address = "%s%s/%s" % (IMAGE_URL, "portrait", img_storage_name)
                    user.save()
                    ManagerLog.objects.create(user_id=request.user.id, type='头像-修改后', msg=model_to_dict(user))
                else:
                    user.portrait_address = "%s%s/%s" % (IMAGE_URL, "portrait", img_storage_name)
                    user.save()
                    ManagerLog.objects.create(user_id=request.user.id, type='头像-上传后', msg=model_to_dict(user))
                return HttpResponseRedirect(reverse('portrait_list'))
        except Exception as e:
            emg = u'头像上传出错'
            logger.error("头像上传出错%s" % e)
            return my_render('juser/portrait_admin_upload.html', locals(), request)

    else:
        return my_render('juser/portrait_admin_upload.html', locals(), request)


@require_role('user')
def portrait_userupload(request):
    header_title, path1, path2 = '上传员工头像', '个人信息', '上传头像'
    user = request.user
    if request.method == 'POST':
        try:
            image = request.FILES.get("portrait", None)
            if image is None:
                return HttpResponseRedirect(reverse('index'))
            else:
                img_size = image.size
                img_url = image.name
                pattern = re.compile(r'(gif|jpg|jpeg|GIF|JPG|JPEG|png)$')
                match = pattern.match(img_url.split('.')[-1])
                if not match:
                    emg = u'请上传gif|jpg|jpeg|GIF|JPG|JPEG|png为后缀的图片'
                    return my_render('juser/portrait_user_upload.html', locals(), request)
                if img_size > FILE_UPLOAD_MAX_SIZE:
                    emg = u'图片大小不能超过%fM' % round(FILE_UPLOAD_MAX_SIZE / 1024.0 / 1024.0, 4)
                    return my_render('juser/portrait_user_upload.html', locals(), request)

                img_url_list = str(image.name).split('.')
                img_storage_name = "%s_%d.%s" % (str(uuid.uuid4().get_hex().lower()[0:8]), user.id, img_url_list[-1])
                image_dir = "%s%s%s" % (BASE_DIR, IMAGE_URL, "portrait")
                if not os.path.exists(image_dir):
                    os.mkdir(image_dir, 755)
                img_storage_path = os.path.join(image_dir, img_storage_name)

                with open(img_storage_path, 'wb+') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
                    f.close()
                if user.portrait_address:
                    ManagerLog.objects.create(user_id=request.user.id, type='头像-修改前', msg=model_to_dict(user))
                    user.portrait_address = "%s%s/%s" % (IMAGE_URL, "portrait", img_storage_name)
                    user.save()
                    ManagerLog.objects.create(user_id=request.user.id, type='头像-修改后', msg=model_to_dict(user))
                else:
                    user.portrait_address = "%s%s/%s" % (IMAGE_URL, "portrait", img_storage_name)
                    user.save()
                    ManagerLog.objects.create(user_id=request.user.id, type='头像-上传后', msg=model_to_dict(user))
                return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            emg = u'头像上传出错'
            logger.error("头像上传出错%s" % e)
            return my_render('juser/portrait_user_upload.html', locals(), request)

    else:
        return my_render('juser/portrait_user_upload.html', locals(), request)


@require_role('admin', 'portrait_list')
def portrait_download(request):
    user_id = request.GET.get('id')
    user = get_object(User, id=user_id)
    if user is not None and user.portrait_address and os.path.exists("%s%s" % (BASE_DIR, user.portrait_address)):
        image_path = "%s%s" % (BASE_DIR, user.portrait_address)
        with open(image_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="image/" + image_path.split('.')[-1].strip())
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(image_path)
            return response
    else:
        return HttpResponseRedirect(reverse('portrait_list'))
