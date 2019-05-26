'''context参数检查装饰器模块'''
import functools

from infra.exceptions import BadRequest


def __check_request(args):
    if not args:
        raise ValueError('该装饰器不能用于无参函数。')
    if args[-1] is None:
        raise ValueError('请给定context参数。')
    context = args[-1]
    if not isinstance(context, dict) or context.get('request', None) is None:
        raise ValueError('未在context参数中指定request，或context类型不为dict。')
    return context.get('request')


def request_required(func):
    '''Check whether request is given or not.'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        __check_request(args)
        return func(*args, **kwargs)
    return wrapper


def admin_required(mode='admin'):
    '''Check whether user is an admin or not.'''
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = __check_request(args)
            if request.user is None:
                raise ValueError('request未指定user。')
            user = request.user
            if mode == 'school_admin':
                if not user.is_school_admin:
                    raise BadRequest('你不是校级管理员。')
            elif mode == 'admin':
                if not user.is_school_admin or not user.is_department_admin:
                    raise BadRequest('你不是管理员。')
            else:
                raise ValueError('装饰器参数错误，mode只能是school_admin'
                                 ' 或者 department_admin')
            return func(*args, **kwargs)
        return wrapper
    return actual_decorator
