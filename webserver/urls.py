from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from webserver.views import index, skin_config, Login, Logout


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^skin_config/$', skin_config, name='skin_config'),
    url(r'^login/$', Login, name='login'),
    url(r'^logout/$', Logout, name='logout'),
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/img/favicon.ico', permanent=True)),
    url(r'^juser/', include('juser.urls')),
    url(r'^jlog/', include('jlog.urls')),
    url(r'^jperm/', include('jperm.urls')),
]
