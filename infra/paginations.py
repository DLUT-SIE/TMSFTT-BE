'''Provide pagination classes for infra module.'''
from rest_framework import pagination

from infra.utils import positive_int
from infra.exceptions import BadRequest


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    '''
    This class is almost identical to
    `rest_frame.pagination.LimitOffsetPagination`, but we allow api consumers
    to disable pagination temporarily by using `limit=-1`.
    '''
    max_limit = 200

    def paginate_queryset(self, queryset, request, view=None):
        '''
        If there are too many objects in the queryset while api consumer
        requires no pagination, we don't allow return without pagination.
        '''
        paginated = super().paginate_queryset(queryset, request, view)
        if paginated is None and self.count > self.max_limit:
            raise BadRequest('不分页前提下查询集合中对象数量超出允许范围')
        return paginated

    def get_limit(self, request):
        '''Get limit, return None if limit param is '-1'.'''
        if self.limit_query_param:
            try:
                limit = request.query_params[self.limit_query_param]
                if limit == '-1':
                    return None
                return positive_int(
                    limit,
                    strict=True,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.default_limit
