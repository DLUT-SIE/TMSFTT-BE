'''Provide API views for mock_cas module.'''
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework_jwt.settings import api_settings


class MockedCASLogoutView(APIView):
    def get(self, request, *args, **kwargs):
        print('CAS Logout!')
        return Response({})


class MockedCASLoginView(APIView):
    '''Provide a list of users can be authenticated as.'''
    renderer_classes = (TemplateHTMLRenderer,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        '''Render a list of users.'''
        # The service user wants to use.
        service = request.query_params.get('service')
        response = Response({
            'users': get_user_model().objects.all(),
            'service': service}, template_name='cas_login_list.html')
        if api_settings.JWT_AUTH_COOKIE:
            response.delete_cookie(api_settings.JWT_AUTH_COOKIE)
        return response


class MockedCASValidateView(APIView):
    '''Provides mocked authentication logic when ticket is given.'''
    renderer_classes = (TemplateHTMLRenderer,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        '''Provide authentication result.'''
        ticket = request.query_params.get('ticket', 'invalid')
        if ticket == 'invalid':
            return Response(
                {}, template_name='cas_authentication_failed_response.xml')
        return Response({'username': ticket},
                        template_name='cas_authentication_success_response.xml')
