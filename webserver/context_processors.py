# coding:utf-8

# from juser.models import User
# from jasset.models import asset, asset_type
from webserver.api import *
from jperm.models import menu_permission


def name_proc(request):
    user_id = request.user.id
    role_id = request.user.role.id
    try:
        menu_obj = menu_permission.objects.prefetch_related('role'). \
            prefetch_related('menu').filter(role_id=role_id, menu__parent__isnull=True).order_by('menu_id')
        c_menu_obj = menu_permission.objects.prefetch_related('role'). \
            prefetch_related('menu').filter(role_id=role_id, menu__parent__isnull=False).order_by('menu_id')
    except Exception as e:
        logger.error('获取用户权限列表异常：%s' % e)
        menu_obj = []
        c_menu_obj = []

    user_total_num = User.objects.all().count()
    user_active_num = User.objects.filter(is_active=1, is_staff=1).count()
    user_induction_num = User.objects.filter(is_active=1, is_staff=0).count()
    user_departure_num = User.objects.filter(is_active=0, is_staff=1).count()
    user_termination_num = User.objects.filter(is_active=0, is_staff=0).count()
    user_positive_num = User.objects.filter(is_active=1, is_staff=1).exclude(id=1).count()
    request.session.set_expiry(3600)

    # for i in menu_obj:
    #     print "====", i.menu.name,i.menu.url,i.menu.code

    info_dic = {'session_user_id': user_id,
                'session_role_id': role_id,
                'user_total_num': user_total_num,
                'user_active_num': user_active_num,
                'user_induction_num': user_induction_num,
                'user_departure_num': user_departure_num,
                'user_termination_num': user_termination_num,
                'user_positive_num': user_positive_num,
                'session_menu_obj': menu_obj,
                'c_session_menu_obj': c_menu_obj,
                'DEVELOPMENT': DEVELOPMENT,
                'VERSION': VERSION
                }

    return info_dic
