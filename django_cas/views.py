"""CAS login/logout replacement views"""
from datetime import datetime
from django.conf import settings
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from django_cas.utils import (
    get_redirect_url,
    get_login_url,
    get_logout_url,
    logout,
)


__all__ = ['LoginView', 'LogoutView']


class LoginView(APIView):
    '''CAS login view, adapted to Django REST framework and JWT.'''
    authentication_classes = ()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        '''Verify ticket issued by CAS server.

        If the ticket is valid, then issue the JWT. ticket and service_url
        should be provided by the request to verify the ticket.
        '''
        if request.user.is_authenticated:
            return HttpResponseRedirect(get_redirect_url(request))
        ticket = request.data.get('ticket')
        service_url = request.data.get('service_url')
        if not ticket or not service_url:
            return HttpResponseForbidden()
        user = auth.authenticate(ticket=ticket, service=service_url)
        if user is not None:
            user.last_login = now()
            user.save()
            # Generage JWT
            payload = api_settings.JWT_PAYLOAD_HANDLER(user)
            token = api_settings.JWT_ENCODE_HANDLER(payload)
            response_data = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER(
                token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response
        if settings.CAS_RETRY_LOGIN:
            # If the ticket is invalid, require another CAS authentication.
            # Only happens when CAS_RETRY_LOGIN is True.
            return HttpResponseRedirect(get_login_url(service_url))
        # Otherwise, return 403 error.
        return HttpResponseForbidden()


class LogoutView(APIView):
    '''Class-based CAS logout view.'''

    def get(self, request):
        '''Log a user out.'''
        logout(request)
        next_page = request.GET.get('next', get_redirect_url(request))
        if settings.CAS_LOGOUT_COMPLETELY:
            next_page = get_logout_url(request, next_page)
        return HttpResponseRedirect(next_page)
