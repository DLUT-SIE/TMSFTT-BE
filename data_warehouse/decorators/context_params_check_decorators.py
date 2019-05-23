'''context参数检查装饰器模块'''
from infra.exceptions import BadRequest
import functools


def __check_request(args):
    if args[-1] is None:
                raise BadRequest('请给定context参数。')
    context = args[-1]
    if context.get('request', None) is None:
        raise BadRequest('未在context参数中指定request。')


def request_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        __check_request(args)
        return func(*args, **kwargs)


def admin_required(mode='department_admin'):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            __check_request(args)
            request = args[-1].get('request')
            assert request is not None
            if request.user is None:
                raise BadRequest('request未指定user。')
            user = request.user
            if mode == 'school_admin':
                if not user.is_school_admin:
                    raise BadRequest('你不是校级管理员。')
            elif mode == 'department_admin':
                if not user.is_school_admin or not user.is_department_admin:
                    raise BadRequest('你不是管理员。')
            else:
                raise BadRequest('装饰器参数错误，mode只能是school_admin'
                                 ' 或者 department_admin')
            return func(*args, **kwargs)
        return wrapper
    return actual_decorator
