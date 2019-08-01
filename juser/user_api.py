# coding: utf-8

# from Crypto.PublicKey import RSA
# from subprocess import call

import xlrd
# from xlrd import xldate_as_tuple
from datetime import datetime
from juser.models import role
from webserver.api import *
from webserver.settings import BASE_DIR, EMAIL_HOST_USER as MAIL_FROM
from jlog.models import ManagerLog
from django.forms.models import model_to_dict


def group_add_user(group_id, user_id=None, username=None):
    """
    用户组中添加用户
    UserGroup Add a user
    """
    if user_id:
        user = get_object(User, id=user_id)
    else:
        user = get_object(User, username=username)

    if user:
        # group.user_set.add(user)
        user.group = UserGroup.objects.get(id=group_id)
        user.save

def db_add_group(**kwargs):
    """
    add a user group in database
    数据库中添加部门
    """
    #获取操作人id
    user_id = kwargs.pop('user_id')

    name = kwargs.get('name')
    group = get_object(UserGroup, name=name)
    parent_id = kwargs.pop('parent')
    dep_admin_id = kwargs.pop('dep_admin')

    try:
        if not group:
            group = UserGroup(**kwargs)
            if parent_id:
                group_parent_obj = UserGroup.objects.get(id=parent_id)
                group.parent = group_parent_obj
            if dep_admin_id:
                dep_admin_obj = User.objects.get(id=dep_admin_id)
                group.dep_admin = dep_admin_obj
            group.save()
            ManagerLog.objects.create(user_id=user_id, type='部门添加', msg=model_to_dict(group))
    except Exception,e:
        logger.error(u"部门 %s 添加失败!" %e)
        # for user_id in users:
        #     group_add_user(group.id, user_id)



def group_update_member(group_id, users_id_list):
    """
    user group update member
    用户组更新成员
    """
    group = get_object(UserGroup, id=group_id)
    if group:
        group.user_set.clear()
        for user_id in users_id_list:
            user = get_object(UserGroup, id=user_id)
            if isinstance(user, UserGroup):
                group.user_set.add(user)


def db_add_user(**kwargs):
    """
    add a user in database
    数据库中添加员工数据
    """
    role_id = kwargs.pop('role')
    group_id = kwargs.pop('groups')
    parent_id = kwargs.pop('parent')
    # position_id = kwargs.pop('position')
    # guide_id = kwargs.pop('guide')
    # empway_id = kwargs.pop('emp_way')
    # entry_time = kwargs.get('entry_time')

    # if entry_time:
    #     pass
    # else:
    #     kwargs.pop('entry_time')

    user = User(**kwargs)
    user.set_password('123456')

    role_obj = role.objects.get(id=role_id)
    user.role = role_obj

    # if guide_id:
    #     guide_obj = User.objects.get(id=guide_id)
    #     user.guide = guide_obj

    # if empway_id:
    #     empway_obj = EmployingWay.objects.get(id=empway_id)
    #     user.emp_way = empway_obj

    if parent_id:
        parent_obj = User.objects.get(id=parent_id)
        user.parent = parent_obj

    # if position_id:
    #     position_obj = userposition.objects.get(id=position_id)
    #     user.position = position_obj

    if group_id:
        group_obj = UserGroup.objects.get(id=group_id)
        user.group = group_obj

    user.save()
    return user


def excel_user_to_db(excel_file, user_id, request):
    try:
        data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
        table = data.sheets()[0]
        rows = table.nrows
        error_dict = {}
        for row_num in range(1, rows):
            row = table.row_values(row_num)
            e_list = []
            if row:
                username, name, guide, job, position_name, emp_way, entry_time, parent_name, group, sex, mobile, wechat = row
                # name = name.encode("utf-8")
                # position_name = position_name.encode("utf-8")

                if '' in [username, name, guide, job, position_name, emp_way, entry_time, group]:
                    e_list.append(u'带*的内容不能为空，请重新编辑后再导入！')
                    error_dict[username] = e_list
                    continue

                if get_object(User, username=username):
                    e_list.append(u'账号: %s 在系统中已存在，请修改后重新导入！' %username)
                    error_dict[username] = e_list
                    continue

                if guide:
                    guide_obj = get_object(User, name=guide)
                    if guide_obj:
                        pass
                    else:
                        e_list.append(u'领带人: %s 不存在，请检查系统中是否存在该员工！' %guide)
                        error_dict[username] = e_list
                        continue

                if position_name:
                    position_obj = get_object(userposition, name=position_name)
                    if position_obj:
                        pass
                    else:
                        e_list.append(u'归属地: %s 不存在，请在系统中新增该归属地再重新导入！' %position_name)
                        error_dict[username] = e_list
                        continue

                if emp_way:
                    emp_obj = get_object(EmployingWay, name=emp_way)
                    if emp_obj:
                        pass
                    else:
                        e_list.append(u'用工方式: %s 填写错误，请修改后再重新导入！' %emp_way)
                        error_dict[username] = e_list
                        continue

                if entry_time:
                    try:
                        entry_time = xlrd.xldate.xldate_as_datetime(entry_time, 0)
                    except Exception,e:
                        e_list.append(u'入职日期格式错误: %s' %e)
                        error_dict[username] = e_list
                        continue

                if group:
                    group_obj = get_object(UserGroup, name=group)
                    if group_obj:
                        pass
                    else:
                        e_list.append(u'直属部门: %s 不存在，请检查系统中是否存在该部门！' %group)
                        error_dict[username] = e_list
                        continue

                if parent_name:
                    parent_obj = get_object(User, name=parent_name)
                    if parent_obj:
                        pass
                    else:
                        e_list.append(u'直属领导: %s 不存在，请检查系统中是否存在该员工！' %parent_name)
                        error_dict[username] = e_list
                        continue

                else:
                    parent_obj = get_object(User, id=group_obj.dep_admin.id)

                uuid_r = uuid.uuid4().get_hex()
                role_obj = get_object(role, id=1)
                email = str(username) + "@huli.com"

                name = name.strip()
                user_obj = User(username=username, name=name, guide=guide_obj, job=job, position=position_obj,
                                emp_way=emp_obj, entry_time=entry_time, parent=parent_obj, group=group_obj,
                                sex=sex, mobile=mobile, wechat=wechat, uuid=uuid_r, role=role_obj, email=email)
                ManagerLog.objects.create(user_id=request.user.id, type='批量导入员工', msg=model_to_dict(user_obj))
                user_obj.save()

        if error_dict:
            dic_len = len(error_dict)
            return error_dict,dic_len
        else:
            return True, row_num
    except Exception, e:
        logger.error(u'解析文件失败：%s' %e)
        dic_len = len(error_dict)
        return error_dict,dic_len


def excel_birthday_to_db(excel_file, request):
    """
    批量导入员工生日
    :param excel_file: 
    :param request: 
    :return: 
    """
    try:
        data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
        table = data.sheets()[0]
        rows = table.nrows
        error_dict = {}
        for row_num in range(1, rows):
            row = table.row_values(row_num)
            e_list = []
            if row:
                name, code, birthday, entry_time = row
                user_obj = get_object(User, code=code)
                name = name.strip()

                if '' in [name, code, birthday, entry_time]:
                    e_list.append(u'带*的内容不能为空，请重新编辑后再导入！')
                    error_dict[code] = e_list
                    continue

                if not user_obj:
                    e_list.append(u'工号对应员工在系统中不存在！')
                    error_dict[code] = e_list
                    continue

                if user_obj.name != name:
                    logger.warning(u'工号%s对应姓名异常, 系统：%s，表格：%s' % (code, user_obj.name, name))
                    e_list.append(u'工号对应姓名异常！')
                    error_dict[code] = e_list
                    continue
                # name = name.encode("utf-8")
                # position_name = position_name.encode("utf-8")

                if entry_time:
                    try:
                        entry_time = xlrd.xldate.xldate_as_datetime(entry_time, 0)
                    except Exception,e:
                        e_list.append(u'入职日期格式错误: %s' %e)
                        error_dict[code] = e_list
                        continue

                if birthday:
                    try:
                        birthday = xlrd.xldate.xldate_as_datetime(birthday, 0)
                    except Exception, e:
                        birthday = time.strptime(birthday, u"%Y年%m月%d日")
                        birthday = time.strftime("%Y-%m-%d", birthday)
                        birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d')
                        # e_list.append(u'出生日期格式错误: %s' % e)
                        # error_dict[code] = e_list
                        # continue

                p_obj = get_object(UserPrivate, user=user_obj)
                if p_obj:
                    continue
                else:
                    p_obj = UserPrivate(user=user_obj, birthday=birthday, entry_time=entry_time)
                    ManagerLog.objects.create(user_id=request.user.id, type='批量导入员工自有信息', msg=model_to_dict(user_obj))
                    p_obj.save()

        if error_dict:
            dic_len = len(error_dict)
            return error_dict, dic_len
        else:
            return True, row_num
    except Exception, e:
        logger.error(u'解析文件失败：%s' %e)
        dic_len = len(error_dict)
        return error_dict, dic_len


def excel_workday_to_db(excel_file, request):
    """
    批量导入员工第一次工作时间
    :param excel_file: 
    :param request: 
    :return: 
    """
    try:
        data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
        table = data.sheets()[0]
        rows = table.nrows
        error_dict = {}
        s_num = 0
        for row_num in range(1, rows):
            row = table.row_values(row_num)
            e_list = []
            if row:
                _, name, code, _, entry_time, graduation_time, work_time, _, _ = row
                code = code.strip()
                user_obj = get_object(User, code=code)
                name = name.strip()

                if '' in [name, code, work_time]:
                    e_list.append(u'带*的内容不能为空，请重新编辑后再导入！')
                    error_dict[code] = e_list
                    continue

                if not user_obj:
                    e_list.append(u'工号对应员工在系统中不存在！')
                    error_dict[code] = e_list
                    continue

                if user_obj.name != name:
                    logger.warning(u'工号%s对应姓名异常, 系统：%s，表格：%s' % (code, user_obj.name, name))
                    e_list.append(u'工号对应姓名异常！')
                    error_dict[code] = e_list
                    continue
                # name = name.encode("utf-8")
                # position_name = position_name.encode("utf-8")

                # try:
                #     work_time = xlrd.xldate.xldate_as_datetime(work_time, 0)
                # except Exception,e:
                #     e_list.append(u'工作日期格式错误: %s' %e)
                #     error_dict[code] = e_list
                #     continue

                try:
                    work_time = xlrd.xldate.xldate_as_datetime(work_time, 0)
                except Exception, e:
                    work_time = time.strptime(work_time, u"%Y年%m月%d日")
                    work_time = time.strftime("%Y-%m-%d", work_time)
                    work_time = datetime.datetime.strptime(work_time, '%Y-%m-%d')

                p_obj = UserPrivate.objects.get_or_create(user=user_obj)[0]
                p_obj.first_work_day = work_time
                ManagerLog.objects.create(user_id=request.user.id, type='批量更新员工自有信息', msg=model_to_dict(user_obj))
                p_obj.save()
                s_num +=1

        if error_dict:
            return error_dict, s_num
        else:
            return True, s_num
    except Exception, e:
        logger.error(u'解析文件失败：%s' %e)
        logger.error(rows)
        return error_dict, s_num


def db_update_user(**kwargs):
    """
    update a user info in database
    数据库更新用户信息
    """
    group_id = kwargs.pop('groups')
    parent_id = kwargs.pop('parent')
    # position_id = kwargs.pop('position')
    # guide_id= kwargs.pop('guide')
    # empway_id = kwargs.pop('empway')
    # admin_groups_post = kwargs.pop('admin_groups')
    user_id = kwargs.pop('user_id')
    user = User.objects.filter(id=user_id)

    if user:
        if parent_id:
            parent_obj = User.objects.get(id=parent_id)
            # user.parent = parent_obj
            kwargs['parent'] = parent_obj
        else:
            User.objects.filter(id=user_id).update(parent=parent_id)
        # if position_id:
        #     position_obj = userposition.objects.get(id=position_id)
        #     # user.position = position_obj
        #     kwargs['position'] = position_obj
        if group_id:
            group_obj = UserGroup.objects.get(id=group_id)
            # user.group = group_obj
            kwargs['group'] = group_obj
        # if guide_id:
        #     guide_obj = User.objects.get(id=guide_id)
        #     kwargs['guide'] = guide_obj
        # if empway_id:
        #     empway_obj = EmployingWay.objects.get(id=empway_id)
        #     kwargs['emp_way'] = empway_obj

        user.update(**kwargs)
        return user[0]

    else:
        return None

    # if user:
    #     user_get = user[0]
    #     password = kwargs.pop('password')
    #     user.update(**kwargs)
    #     if password.strip():
    #         user_get.set_password(password)
    #         user_get.save()
    # else:
    #     return None

    # group_select = []
    # if groups_post:
    #     for group_id in groups_post:
    #         group = UserGroup.objects.filter(id=group_id)
    #         group_select.extend(group)
    # user_get.group = group_select

    # if admin_groups_post != '':
    #     user_get.admingroup_set.all().delete()
    #     for group_id in admin_groups_post:
    #         group = get_object(UserGroup, id=group_id)
    #         AdminGroup(user=user, group=group).save()


def db_del_user(username):
    """
    delete a user from database
    从数据库中删除用户
    """
    user = get_object(User, username=username)
    if user:
        user.delete()


def gen_ssh_key(username, password='',
                key_dir=os.path.join(KEY_DIR, 'user'),
                authorized_keys=True, home="/home", length=2048):
    """
    generate a user ssh key in a property dir
    生成一个用户ssh密钥对
    """
    logger.debug('生成ssh key， 并设置authorized_keys')
    private_key_file = os.path.join(key_dir, username+'.pem')
    mkdir(key_dir, mode=777)
    if os.path.isfile(private_key_file):
        os.unlink(private_key_file)
    ret = bash('echo -e  "y\n"|ssh-keygen -t rsa -f %s -b %s -P "%s"' % (private_key_file, length, password))

    if authorized_keys:
        auth_key_dir = os.path.join(home, username, '.ssh')
        mkdir(auth_key_dir, username=username, mode=700)
        authorized_key_file = os.path.join(auth_key_dir, 'authorized_keys')
        with open(private_key_file+'.pub') as pub_f:
            with open(authorized_key_file, 'w') as auth_f:
                auth_f.write(pub_f.read())
        os.chmod(authorized_key_file, 0600)
        chown(authorized_key_file, username)


def server_add_user(username, ssh_key_pwd=''):
    """
    add a system user in webserver
    在webserver服务器上添加一个用户
    """
    bash("useradd -s '%s' '%s'" % (os.path.join(BASE_DIR, 'init.sh'), username))
    gen_ssh_key(username, ssh_key_pwd)


# def user_add_mail(user, kwargs):
#     """
#     add user send mail
#     发送用户添加邮件
#     """
#     user_role = {'SU': u'超级管理员', 'GA': u'组管理员', 'CU': u'普通用户'}
#     mail_title = u'恭喜你的跳板机用户 %s 添加成功 webserver' % user.name
#     mail_msg = u"""
#     Hi, %s
#         您的用户名： %s
#         您的权限： %s
#         您的web登录密码： %s
#         您的ssh密钥文件密码： %s
#         密钥下载地址： %s/juser/key/down/?uuid=%s
#         说明： 请登陆跳板机后台下载密钥, 然后使用密钥登陆跳板机！
#     """ % (user.name, user.username, user_role.get(user.role, u'普通用户'),
#            kwargs.get('password'), kwargs.get('ssh_key_pwd'), URL, user.uuid)
#     send_mail(mail_title, mail_msg, MAIL_FROM, [user.email], fail_silently=False)


def server_del_user(username):
    """
    delete a user from webserver linux system
    删除系统上的某用户
    """
    bash('userdel -r -f %s' % username)
    logger.debug('rm -f %s/%s_*.pem' % (os.path.join(KEY_DIR, 'user'), username))
    bash('rm -f %s/%s_*.pem' % (os.path.join(KEY_DIR, 'user'), username))
    bash('rm -f %s/%s.pem*' % (os.path.join(KEY_DIR, 'user'), username))


def get_display_msg(user, password='', ssh_key_pwd='', send_mail_need=False):
    if send_mail_need:
        msg = u'添加用户 %s 成功！ 用户密码已发送到 %s 邮箱！' % (user.name, user.email)
    else:
        msg = u"""
        跳板机地址： %s <br />
        用户名：%s <br />
        密码：%s <br />
        密钥密码：%s <br />
        密钥下载url: %s/juser/key/down/?uuid=%s <br />
        该账号密码可以登陆web和跳板机。
        """ % (URL, user.username, password, ssh_key_pwd, URL, user.uuid)
    return msg



def get_user_data(request, **kwargs):
    """
    根据用户权限返回用户信息
    :param request: 
    :return: 
    """
    if request.user.role.code == 'CU':
        user_obj = User.objects.filter(id=request.user.id)
        if kwargs == {}:
            pass
        else:
            user_obj = user_obj.filter(**kwargs)
    else:
        menu_permission_obj = menu_permission.objects.filter(role_id=request.user.role.id, menu_id=1)
        if menu_permission_obj:
            if kwargs == {}:
                user_obj = User.objects.all()
            else:
                user_obj = User.objects.filter(**kwargs)
        else:
            user_obj = User.objects.filter(id=request.user.id)
    return user_obj