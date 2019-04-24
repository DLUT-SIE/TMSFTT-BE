'''Define various exceptions used in TMSFTT.'''
from rest_framework import exceptions, status


class BadRequest(exceptions.APIException):
    '''Exception for BadRequest (400)'''
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'bad_request'


class InternalServerError(exceptions.APIException):
    '''Exception for InternalServerError (500)'''
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = 'internal_server_error'
