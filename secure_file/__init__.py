'''Define constants used across this app.'''
from django.conf import settings


SECURE_FILE_PREFIX = f'{settings.MEDIA_URL.strip("/")}/secure'
INSECURE_FILE_PREFIX = f'{settings.MEDIA_URL.strip("/")}/insecure'
