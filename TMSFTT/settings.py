"""
Django settings for TMSFTT project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework_bulk',
    'django_filters',
    'django_cas',
    "guardian",

    'secure_file',
    'drf_cache',
    'auth.apps.AuthConfig',
    'infra',
    'training_program',
    'training_event',
    'training_record',
    'training_review',
    'data_warehouse',
    'tiny_url',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'auth.middleware.JWTAuthenticationMiddleware',
    'django_cas.middleware.CASMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
    'guardian.backends.ObjectPermissionBackend',
]

AUTH_USER_MODEL = 'tmsftt_auth.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'auth.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    #     'infra.utils.BrowsableAPIRendererWithoutForms',
    # ),
    # At least we require all users to have been authenticated.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'UPLOADED_FILES_USE_URL': False,
    'DEFAULT_PAGINATION_CLASS': 'infra.paginations.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'HTML_SELECT_CUTOFF': 100,
    'DATETIME_FORMAT': '%Y年%m月%d日 %H:%M:%S',
    'DATETIME_INPUT_FORMATS': ['%Y年%m月%d日 %H:%M:%S', 'iso-8601'],
}

ROOT_URLCONF = 'TMSFTT.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TMSFTT.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'


# JWT settings
JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_GET_USER_SECRET_KEY': 'auth.utils.get_user_secret_key',
    'JWT_AUDIENCE': 'TMSFTT clients',
    'JWT_ISSUER': 'TMSFTT server',
    'JWT_AUTH_COOKIE': 'ACCESS_TOKEN',
    'JWT_ALLOW_REFRESH': True,
    # JWT expires in 18 hours.
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=12),
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'auth.utils.jwt_response_payload_handler',
}
JWT_AUTH_COOKIE = JWT_AUTH['JWT_AUTH_COOKIE']
JWT_AUTH_COOKIE_WHITELIST = (
    '/media/',
)

# Email settings

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SOAP settings
SOAP_BASE_URL = 'http://****/service'
SOAP_AUTH_TP_NAME = 'unknown'
SOAP_AUTH_SYS_ID = 'unknown'
SOAP_AUTH_MODULE_ID = 'unknown'
SOAP_AUTH_SECRET_KEY = 'unknown'
SOAP_AUTH_INTERFACE_METHOD = 'unknown'


# Site settings
SITE_ID = 1
