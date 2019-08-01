# ~*~ coding: utf-8 ~*~

from __future__ import absolute_import, unicode_literals
import os

from celery import Celery, platforms
from celery.schedules import crontab
from jumpserver.settings import DEVELOPMENT

# init system environ
platforms.C_FORCE_ROOT = True
platforms.PYTHONOPTIMIZE = True

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jumpserver.settings')

app = Celery('jumpserver')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

# app.conf.task_routes = {
#     'jcoin.tasks.*': {'queue': 'jcoin'},
# }

app.conf.beat_schedule = {
    'celery_cron_task': {
        'task': 'jcoin.tasks.do_bid_confirm',
        'schedule': crontab(minute='*/3'),
        'args': (),
    },
}
