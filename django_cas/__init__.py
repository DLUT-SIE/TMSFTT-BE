"""CAS backend, adapted to Django REST framework and JWT."""
from django.conf import settings

__all__ = []

_DEFAULTS = {
    'CAS_ADMIN_PREFIX': None,
    'CAS_EXTRA_LOGIN_PARAMS': None,
    'CAS_FRONTEND_LOGIN_URL': '/auth/login/',
    'CAS_IGNORE_REFERER': False,
    'CAS_LOGOUT_COMPLETELY': True,
    'CAS_REDIRECT_URL': '/',
    'CAS_RETRY_LOGIN': False,
    'CAS_SERVER_URL': None,
    'CAS_VERSION': '2',
}

for key, value in _DEFAULTS.items():
    if hasattr(settings, key):  # pragma: no cover
        continue
    setattr(settings, key, value)
