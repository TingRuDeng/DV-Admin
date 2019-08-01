from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView


urlpatterns = patterns('webserver.views',
                       url(r'^$', 'index', name='index'),
                       url(r'^skin_config/$', 'skin_config', name='skin_config'),
                       url(r'^login/$', 'Login', name='login'),
                       url(r'^logout/$', 'Logout', name='logout'),
                       url(r'^favicon.ico$', RedirectView.as_view(url=r'static/img/favicon.ico', permanent=True)),
                       url(r'^juser/', include('juser.urls')),
                       # url(r'^jcard/', include('jcard.urls')),
                       url(r'^jlog/', include('jlog.urls')),
                       url(r'^jperm/', include('jperm.urls')),
                       )
