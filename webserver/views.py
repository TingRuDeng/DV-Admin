# coding: utf-8

from __future__ import division

from django.db.models import Count
from webserver.api import *
from django.contrib.auth import authenticate, login, logout
from jlog.models import Log


def getDaysByNum(num):
    """
    输出格式:([datetime.date(2015, 11, 6),  datetime.date(2015, 11, 8)], ['11-06', '11-08'])
    """

    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    date_li, date_str = [], []
    for i in range(0, num):
        today = today-oneday
        date_li.append(today)
        date_str.append(str(today)[5:10])
    date_li.reverse()
    date_str.reverse()
    return date_li, date_str


def get_data_by_day(date_li, item):
    data_li = []
    for d in date_li:
        logs = Log.objects.filter(start_time__year=d.year,
                                  start_time__month=d.month,
                                  start_time__day=d.day)
        if item == 'user':
            data_li.append(set([log.user for log in logs]))
        elif item == 'asset':
            data_li.append(set([log.host for log in logs]))
        elif item == 'login':
            data_li.append(logs)
        else:
            pass
    return data_li


def get_count_by_day(date_li, item):
    data_li = get_data_by_day(date_li, item)
    data_count_li = []
    for data in data_li:
        data_count_li.append(len(data))
    return data_count_li


def get_count_by_date(date_li, item):
    data_li = get_data_by_day(date_li, item)
    data_count_tmp = []
    for data in data_li:
        data_count_tmp.extend(list(data))

    return len(set(data_count_tmp))


@require_role(role='user')
def index_cu(request):
    # username = request.user.username
    return HttpResponseRedirect(reverse('user_detail'))


@require_role(role='user')
def index(request):
    li_date, li_str = getDaysByNum(7)
    today = datetime.datetime.now().day
    from_week = datetime.datetime.now() - datetime.timedelta(days=7)

    if request.user.role.code in ['CU', 'GA']:
        return HttpResponseRedirect(reverse('user_detail'))

    if request.user.role.code == 'SU':
        # dashboard 显示汇总
        users = User.objects.filter(is_active=True, is_staff=True)
        # hosts = asset.objects.exclude(status_id=6)
        online = Log.objects.filter(is_finished=0)
        online_host = online.values('host').distinct()
        # online_user = online.values('user').distinct()
        # login_user = get_recent_login(7)
        active_users = User.objects.filter(is_active=1)
        # active_hosts = Assets.objects.filter(is_active=1)

        # 一个月历史汇总
        date_li, date_str = getDaysByNum(30)
        date_month = repr(date_str)
        active_user_per_month = str(get_count_by_day(date_li, 'user'))
        active_asset_per_month = str(get_count_by_day(date_li, 'asset'))
        active_login_per_month = str(get_count_by_day(date_li, 'login'))

        # 活跃用户资产图
        active_user_month = get_count_by_date(date_li, 'user')
        disabled_user_count = len(users.filter(is_active=False))
        inactive_user_month = len(users) - active_user_month
        active_asset_month = get_count_by_date(date_li, 'asset')
        # disabled_asset_count = len(hosts.filter(is_active=False)) if hosts.filter(is_active=False) else 0
        # inactive_asset_month = len(hosts) - active_asset_month if len(hosts) > active_asset_month else 0

        # 一周top10用户和主机
        week_data = Log.objects.filter(start_time__range=[from_week, datetime.datetime.now()])

        # 一周top5
        week_users = week_data.values('user').distinct().count()
        week_hosts = week_data.count()

        user_top_five = week_data.values('user').annotate(times=Count('user')).order_by('-times')[:5]
        color = ['label-success', 'label-info', 'label-primary', 'label-default', 'label-warnning']

        return render(request, 'index.html', locals())
    return HttpResponseRedirect(reverse('user_detail'))


def skin_config(request):
    return render_to_response('skin_config.html')


@defend_attack
def Login(request):
    """登录界面"""
    error = ''
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'GET':
        return render_to_response('login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user.role is None:
                        return render_to_response('login.html')
                    if user.role.code == 'SU':
                        request.session['role_id'] = 2
                    elif user.role.code == 'CU':
                        request.session['role_id'] = 1
                    else:
                        request.session['role_id'] = 0
                    return HttpResponseRedirect(request.session.get('pre_url', '/'))
                else:
                    error = u'用户未激活'
            else:
                error = u'用户名或密码错误'
        else:
            error = u'用户名或密码错误'
    return render_to_response('login.html', {'error': error})


@require_role('user')
def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
