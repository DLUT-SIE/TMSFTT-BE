import os
import os.path as osp

from .settings import *


def get_secret_from_file(file_env_name, default=None):
    path = os.environ.get(file_env_name, None)
    if path is None:
        if default is None:
            raise ValueError('{} is not provided'.format(file_env_name))
        return default
    with open(path) as f:
        return f.read().strip()


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret_from_file('SECRET_KEY_FILE')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost']
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
CONN_MAX_AGE = 10

# DRF settings
REST_FRAMEWORK.update(
    'DEFAULT_RENDERER_CLASSES',
    (
        'rest_framework.renderers.JSONRenderer',
    )
)


# User-uploaded files
MEDIA_ROOT = '/media/'
MEDIA_URL = '/media/'

# CAS dev settings
CAS_SERVER_URL = 'http://localhost:8000/mock-cas/'
CAS_IGNORE_REFERER = True
CAS_REDIRECT_URL = '/'

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True


# HTTPS
# TODO(youchen): Enable HTTPS secure
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
