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

# TODO(youchen): Remove mock_cas app
DEV_INSTALLED_APPS = [
    'mock_cas',
]
INSTALLED_APPS.extend(DEV_INSTALLED_APPS)

# Middlewares
MIDDLEWARE.extend([
    'infra.middleware.OperationLogMiddleware',
])


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret_from_file('SECRET_KEY_FILE')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', '39.98.197.214']
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


# DRF settings
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
)

# Dynamic contents
MEDIA_ROOT = '/protected-files/'
MEDIA_URL = '/media/'

# CAS dev settings
CAS_SERVER_URL = 'https://39.98.197.214/mock-cas/'
CAS_IGNORE_REFERER = True
CAS_REDIRECT_URL = '/'

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True


# HTTPS
# TODO(youchen): Enable HTTPS secure
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Celery settings
CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_BEAT_SCHEDULE = {
    'update_teachers_and_departments_information': {
        'task': 'auth.tasks.update_teachers_and_departments_information',
        'schedule': crontab(minute=0, hour=0)  # Daily at midnight.
    },
    'generate_user_rankings': {
        'task': 'data_warehouse.tasks.generate_user_rankings',
        'schedule': crontab(minute=10, hour=0)  # Daily at midnight.
    }
}

# Email settings

EMAIL_BACKEND = 'infra.backends.SOAPEmailBackend'

# JWT settings
# Disable cookies for JWT in prod environment to prevent CSRF, we allow
# this to help debug in browsable API.
JWT_AUTH['JWT_AUTH_COOKIE'] = None

# SOAP settings
# TODO(youchen): Update to prod settings
SOAP_BASE_URL = 'http://message.dlut.edu.cn/mp/service'
SOAP_AUTH_TP_NAME = 'unknown'
SOAP_AUTH_SYS_ID = 'unknown'
SOAP_AUTH_MODULE_ID = 'unknown'
SOAP_AUTH_SECRET_KEY = 'unknown'
SOAP_AUTH_INTERFACE_METHOD = 'unknown'
