import os
import os.path as osp

from .settings import *

from celery.schedules import crontab


def get_secret_from_file(file_env_name, default=None):
    path = os.environ.get(file_env_name, None)
    if path is None:
        if default is None:
            raise ValueError('{} is not provided'.format(file_env_name))
        return default
    with open(path) as f:
        return f.read().strip()


# Middlewares
MIDDLEWARE.extend([
    'infra.middleware.OperationLogMiddleware',
])


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret_from_file('SECRET_KEY_FILE')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', 'test.feingst.com', 'ctfdpeixun.dlut.edu.cn']
INTERNAL_IPS = ['127.0.0.1']

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME', 'TMSFTT'),
        'USER': os.environ.get('DATABASE_USER', 'root'),
        'PASSWORD': get_secret_from_file('DATABASE_PASSWORD_FILE'),
        'HOST': os.environ.get('DATABASE_HOST', 'tmsftt-db'),
        'PORT': os.environ.get('DATABASE_PORT', '3306'),
        'CONN_MAX_AGE': 10,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'TEST': {
            'NAME': 'TMSFTT_TEST',
            'CHARSET': 'UTF8MB4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {filename}(L{lineno:d}) {process:d}: {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'django.server': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '/django-server.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.prod': {
            'handlers': ['django.server', 'file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

# A list of all the people who get code error notifications.
ADMINS = [

]


# DRF settings
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
)

# Dynamic contents
MEDIA_ROOT = '/protected-files/'
MEDIA_URL = '/media/'

# CAS dev settings
CAS_SERVER_URL = 'https://sso.dlut.edu.cn/cas/'
CAS_IGNORE_REFERER = True
CAS_REDIRECT_URL = '/'
CAS_LOGOUT_COMPLETELY = True

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True


# Celery settings
CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_BEAT_SCHEDULER = 'celery.schedulers.DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {
    'update_teachers_and_departments_information': {
        'task': 'auth.tasks.update_teachers_and_departments_information',
        'schedule': crontab(minute=0, hour=0)  # Daily at midnight.
    },
    'generate_user_rankings': {
        'task': 'data_warehouse.tasks.generate_user_rankings',
        'schedule': crontab(minute=10, hour=0)  # Daily at midnight.
    },
    'send_mail_to_inactive_users': {
        'task': 'data_warehouse.tasks.send_mail_to_inactive_users',
        # Every year
        'schedule': crontab(minute=0, hour=1, day_of_month=1, month_of_year=1)
    },
    'send_mail_to_users_with_events_next_day': {
        'task': 'data_warehouse.tasks.send_mail_to_users_with_events_next_day',
        'schedule': crontab(minute=0, hour=7)  # Daily at moring.
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Email settings

EMAIL_BACKEND = 'infra.backends.SOAPEmailBackend'

# JWT settings
# Disable cookies for JWT in prod environment to prevent CSRF, we allow
# this to help debug in browsable API.
JWT_AUTH_COOKIE = None

# SOAP settings
# TODO(youchen): Update to prod settings
SOAP_BASE_URL = 'http://message.dlut.edu.cn/mp/service'
SOAP_AUTH_TP_NAME = 'ctfdpeixun'
SOAP_AUTH_SYS_ID = 'mp'
SOAP_AUTH_MODULE_ID = 'email'
SOAP_AUTH_SECRET_KEY = get_secret_from_file('SOAP_AUTH_SECRET_KEY_FILE')
