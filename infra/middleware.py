'''Middlewares provided by infra module.'''
from django.utils.deprecation import MiddlewareMixin

from infra.models import OperationLog


# pylint: disable=too-few-public-methods
class OperationLogMiddleware(MiddlewareMixin):
    '''Store logs for unsafe requests in database.'''
    SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS'}

    def process_response(self, request, response):
        '''Create OperationLog for unsafe HTTP methods.'''
        if request.method not in self.SAFE_METHODS:
            OperationLog.from_response(request, response).save()
        return response
