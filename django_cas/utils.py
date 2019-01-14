'''Utility functions for django_cas module.'''
from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME


def get_redirect_url(request):
    """
    Redirects to referring page, or CAS_REDIRECT_URL if no referrer is set.
    """
    next_page = request.GET.get(REDIRECT_FIELD_NAME)
    if not next_page:
        if settings.CAS_IGNORE_REFERER:
            next_page = settings.CAS_REDIRECT_URL
        else:
            next_page = request.META.get('HTTP_REFERER',
                                         settings.CAS_REDIRECT_URL)
        prefix = (('http://', 'https://')[request.is_secure()] +
                  request.get_host())
        if next_page.startswith(prefix):
            next_page = next_page[len(prefix):]
    return next_page


def get_login_url(service):
    """Generates CAS login URL"""
    params = {'service': service}
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    return urljoin(settings.CAS_SERVER_URL, 'login') + '?' + urlencode(params)


def get_logout_url(request, next_page=None):
    """Generates CAS logout URL"""
    url = urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urlencode({'url': protocol + host + next_page})
    return url


def logout(request):
    '''Log out a user, in JWT way.'''
    if request.user.is_authenticated:
        # In our case, this would set a new random password to user,
        # which would invalidate the user's JWT.
        user = request.user
        user.set_unusable_password()
        user.save()
