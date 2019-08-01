from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from jumpserver.views import index, skin_config, Login, Logout, user_index, mail_info


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^index/detail/$', user_index, name='user_index'),
    url(r'^index/mail/$', mail_info, name='mail_info'),
    url(r'^skin_config/$', skin_config, name='skin_config'),
    url(r'^login/$', Login, name='login'),
    url(r'^logout/$', Logout, name='logout'),
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/img/favicon.ico', permanent=True)),
    url(r'^juser/', include('juser.urls')),
    url(r'^jlog/', include('jlog.urls')),
    url(r'^jperm/', include('jperm.urls')),
    ]
