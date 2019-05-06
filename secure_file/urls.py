'''URL mappings for secure_file module.'''
from django.urls import re_path, path, include
from rest_framework import routers

from secure_file import SECURE_FILE_PREFIX, INSECURE_FILE_PREFIX
from secure_file.views import (
    SecuredFileDownloadView,
    InSecuredFileDownloadView,
    InSecureFileViewSet
)


router = routers.SimpleRouter()
router.register('insecure-files', InSecureFileViewSet,
                base_name='insecure-files')

# /media/secure/xxx
SECURE_FILE_RE_PATH = f'^{SECURE_FILE_PREFIX}/(?P<encrypted_path>.+)$'
# /media/insecure/xxx
INSECURE_FILE_RE_PATH = f'^{INSECURE_FILE_PREFIX}/(?P<file_id>.+)$'

urlpatterns = [
    re_path(SECURE_FILE_RE_PATH, SecuredFileDownloadView.as_view(),
            name='secure-file-download'),
    re_path(INSECURE_FILE_RE_PATH, InSecuredFileDownloadView.as_view(),
            name='insecure-file-download'),
    path('api/', include(router.urls)),
]
