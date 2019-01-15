import os.path as osp

from .settings import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0jn@1=-wjx6zt)vg7^s9=g-yads8qrwy5*(r#a$*pbf2o11d(h'


# Application definition
DEV_INSTALLED_APPS = [
    'debug_toolbar',
    'mock_cas',
]
INSTALLED_APPS.extend(DEV_INSTALLED_APPS)

DEV_MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
MIDDLEWARE.extend(DEV_MIDDLEWARE)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'TMSFTT',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'TEST': {
            'NAME': 'TMSFTT_TEST',
            'CHARSET': 'UTF8MB4',
            'COLLATION': 'utf8mb4_general_ci',
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

# User-uploaded files
MEDIA_ROOT = osp.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# CAS dev settings
CAS_SERVER_URL = 'http://localhost:8000/mock-cas/'
CAS_IGNORE_REFERER = True
CAS_REDIRECT_URL = '/'
