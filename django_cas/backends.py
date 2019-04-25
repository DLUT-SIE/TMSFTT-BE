"""CAS authentication backend"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from django_cas.cas_protocols import CAS_PROTOCOLS


__all__ = ['CASBackend']
User = get_user_model()
if settings.CAS_VERSION not in CAS_PROTOCOLS:  # pragma: no cover
    raise ValueError('Unsupported CAS_VERSION %r' % settings.CAS_VERSION)
CAS_VERIFY = CAS_PROTOCOLS[settings.CAS_VERSION]


class CASBackend(ModelBackend):  # pylint: disable=R0903
    """CAS authentication backend"""
    def authenticate(self, request, ticket, service):  # pylint: disable=W0221
        """Verifies CAS ticket and gets or creates User object"""
        username, _ = CAS_VERIFY(ticket, service)
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        return user
