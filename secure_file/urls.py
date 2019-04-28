'''URL mappings for secure_file module.'''
from django.urls import re_path
from django.conf import settings

from secure_file.views import SecuredFileDownloadView


MEDIA_URL = '^{}/(?P<encrypted_url>.+)$'.format(settings.MEDIA_URL.strip('/'))

urlpatterns = [
    re_path(MEDIA_URL, SecuredFileDownloadView.as_view(),
            name='secured-file-download'),
]
