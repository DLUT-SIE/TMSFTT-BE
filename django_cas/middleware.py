"""CAS authentication middleware"""
from urllib.parse import urlencode
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse

from django_cas.views import (
    LoginView as CASLoginView,
    LogoutView as CASLogoutView,
)


__all__ = ['CASMiddleware']


class CASMiddleware(MiddlewareMixin):
    """Middleware that allows CAS authentication on admin pages"""

    def process_request(self, request):  # pylint: disable=R0201
        """Checks that the authentication middleware is installed"""

        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        assert hasattr(request, 'user'), error

    def process_view(self, request, view_func,  # pylint: disable=R0911,R0201
                     view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """
        # Only class-based login and logout views are supported
        if hasattr(view_func, 'view_class'):
            if view_func.view_class == LoginView:  # pylint: disable=R1705
                return HttpResponseRedirect(reverse('cas-login'))
            elif view_func.view_class == LogoutView:
                return HttpResponseRedirect(reverse('cas-logout'))
            elif view_func.view_class in (CASLoginView, CASLogoutView):
                return None

        # Request is not for admin console, do nothing.
        if settings.CAS_ADMIN_PREFIX:
            if not request.path.startswith(settings.CAS_ADMIN_PREFIX):
                return None
        elif not view_func.__module__.startswith('django.contrib.admin.'):
            return None

        # Request is for admin console, and it is authenticated.
        if request.user.is_authenticated:
            if request.user.is_staff:
                # Only staff can access admin console
                return None
            # Not a staff, forbidden
            error = ('<h1>Forbidden</h1><p>You do not have staff '
                     'privileges.</p>')
            return HttpResponseForbidden(error)
        # Otherwise, redirect to login.
        params = urlencode({REDIRECT_FIELD_NAME: request.get_full_path()})
        return HttpResponseRedirect(reverse('cas-login') + '?' + params)
