"""
Django settings for webserver project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from __future__ import absolute_import
import os
import ldap
import ConfigParser
from django_auth_ldap.config import LDAPSearch

config = ConfigParser.ConfigParser()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
config.read(os.path.join(BASE_DIR, 'webserver.conf'))
KEY_DIR = os.path.join(BASE_DIR, 'keys')


# add ldap backend
if config.get('ldap', 'enable'):
    try:
        AUTH_LDAP_SERVER_URI = config.get('ldap', 'ldap_server')
    except ConfigParser.NoOptionError:
        AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1"
    AUTH_LDAP_CONNECTION_OPTIONS = {
        ldap.OPT_REFERRALS: 0,
        ldap.OPT_DEBUG_LEVEL: 1,
        ldap.OPT_TIMEOUT: 25,
    }

    AUTH_LDAP_BIND_DN = config.get('ldap', 'ldap_bind_dn')
    AUTH_LDAP_BIND_PASSWORD = config.get('ldap', 'ldap_bind_password')
    AUTH_LDAP_USER_SEARCH = LDAPSearch(config.get('ldap', 'ldap_search_dn'),
                                       ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")
    AUTH_LDAP_USER_ATTR_MAP = {
        "name": "displayName",
        # "uuid": "sAMAccountName",
        # "first_name": "givenName",
        "last_name": "sn",
        "email": "mail"
    }
    AUTH_LDAP_ALWAYS_UPDATE_USER = True
    AUTH_LDAP_FIND_GROUP_PERMS = False

    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
    )
else:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )
# end

AUTH_USER_MODEL = 'juser.User'

# mail config
MAIL_ENABLE = config.get('mail', 'mail_enable')
EMAIL_HOST = config.get('mail', 'email_host')
EMAIL_PORT = config.get('mail', 'email_port')
EMAIL_HOST_USER = config.get('mail', 'email_host_user')
EMAIL_HOST_PASSWORD = config.get('mail', 'email_host_password')
EMAIL_USE_TLS = config.getboolean('mail', 'email_use_tls')
try:
    EMAIL_USE_SSL = config.getboolean('mail', 'email_use_ssl')
except ConfigParser.NoOptionError:
    EMAIL_USE_SSL = False
EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend' if EMAIL_USE_SSL else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_TIMEOUT = 5

# ======== Log ==========
LOG_DIR = os.path.join(BASE_DIR, 'logs')
KEY = config.get('base', 'key')
URL = config.get('base', 'url')
LOG_LEVEL = config.get('base', 'log')
IP = config.get('base', 'ip')
PORT = config.get('base', 'port')
DEVELOPMENT = config.getboolean('base', 'develop')
VERSION = config.get('base', 'version')

# ====== alert ======
AlertUrl = config.get('alert', 'alert_url')

# # ====== redis =======
# RedisServer = config.get('redis', 'redis_server')
# RedisPort = config.get('redis', 'redis_port')
# RedisPassword = config.get('redis', 'redis_password')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!%=t81uof5rhmtpi&(zr=q^fah#$enny-c@mswz49l42j0o49-'

# SECURITY WARNING: don't run with debug turned on in production!
if DEVELOPMENT:
    DEBUG = True
else:
    DEBUG = False

# TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_crontab',
    'bootstrapform',
    'djcelery',
    'webserver',
    'juser',
    'jperm',
    'jlog',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'webserver.urls'

WSGI_APPLICATION = 'webserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {}
if config.get('db', 'engine') == 'mysql': 
    DB_HOST = config.get('db', 'host')
    DB_PORT = config.getint('db', 'port')
    DB_USER = config.get('db', 'user')
    DB_PASSWORD = config.get('db', 'password')
    DB_DATABASE = config.get('db', 'database')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': DB_DATABASE,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }
elif config.get('db', 'engine') == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': config.get('db', 'database'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'webserver.context_processors.name_proc',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
IMAGE_URL = os.path.join(STATIC_URL, 'image/')

BOOTSTRAP_COLUMN_COUNT = 10

# CRONJOBS = [
    # ('0 1 * * *', 'jasset.asset_api.asset_ansible_update_all'),
    # ('*/10 * * * *', 'jlog.log_api.kill_invalid_connection'),
    # ('00 04 * * *', 'jattendance.attendance_api.atten_process_data'),
    # ('00 22 * * *', 'jattendance.attendance_api.atten_process_data'),
# ]

# CELERY_IMPORTS = ('jattendance.tasks.attendance_quest_task',)

# import djcelery
# from datetime import timedelta
# from celery.schedules import crontab
# from celery import platforms
# from kombu import Exchange, Queue
#
# platforms.C_FORCE_ROOT = True
# CELERY_TIMEZONE = TIME_ZONE
# djcelery.setup_loader()
# # BROKER_URL = 'redis://:123456@192.168.10.24:6379/1'
# # CELERY_RESULT_BACKEND = 'redis://:123456@192.168.10.24:6379/1'
#
# # ------ celery
# BROKER_URL = 'redis://:%(password)s@%(host)s:%(port)s/5' % {
#         'password': RedisPassword,
#         'host': RedisServer,
#         'port': RedisPort,
#     }
# CELERY_RESULT_BACKEND = BROKER_URL
# CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
#
# CELERY_QUEUES = (
#     Queue('default', Exchange('default'), routing_key='default'),
#     Queue('for_task_collect', Exchange('for_task_collect'), routing_key='for_task_collect'),
# )
#
# CELERY_DEFAULT_QUEUE = 'default'
# CELERY_DEFAULT_EXCHANGE = 'default'
# CELERY_DEFAULT_ROUTING_KEY = 'default'
#
# CELERY_ROUTES = {
#     # 'jact.tasks.giftquest_add': {'queue': 'for_task_collect', 'routing_key': 'for_task_collect'},
# }
#
# CELERYBEAT_SCHEDULE={
#     # 'gift_quest_task': {
#     #     'task': 'jact.tasks.giftquest_add',
#     #     'schedule': crontab(day_of_month='20', hour='08', minute='00'),
#     #     'args': (),
#     # },
#     # 'birthday_wisher_task': {
#     #     'task': 'jact.tasks.birthday_wisher',
#     #     'schedule': crontab(minute=00, hour=9),
#     #     'args': (),
#     # }
# }
# CELERYBEAT_SCHEDULE={
#     'attendance_quest_task': {
#         'task': 'jattendance.tasks.attendance_quest_task',
#         'schedule': crontab(minute=0, hour=0),
#         'args': (),
#     }
# }

# from datetime import timedelta
#
#
# CELERYBEAT_SCHEDULE = {
#     'add-every-3-seconds': {
#         'task': 'jmeet.tasks.test_celery',
#         # 'schedule': crontab(minute=u'40', hour=u'17',),
#         'schedule': timedelta(seconds=3),
#         'args': (16, 16)
#     },
#     # 'timing': {
#     #     'task': 'jmeet.tasks.test_multiply',
#     #     'schedule': crontab(minute=u'28', hour=u'11',),
#     #     # 'schedule': timedelta(seconds=3),
#     #     'args': (2, 3)
#     # },
# }
FILE_UPLOAD_MAX_SIZE = 2 * 1024 * 1024
