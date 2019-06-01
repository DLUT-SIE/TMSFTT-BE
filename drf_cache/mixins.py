'''Mixins that provide cache support for DRF.'''
from django.core.cache import cache
from django.db.models import signals

from drf_cache import CACHE_TIMEOUT
from drf_cache.utils import (
    build_cache_key, invalidate_all_caches
)


class DRFCacheMixin:
    '''Cache DRF responses of list, retrieve.

    Properties
    ----------
    timeout: int
        The number of seconds before deleting the cached result. Default: 600
    '''
    timeout = CACHE_TIMEOUT
    _signals_registered = False

    @staticmethod
    def __is_paginated_response(data):
        res = (x in data for x in ('count', 'previous', 'next', 'results'))
        return all(res)

    def _build_cache_for_results(self, cache_key, response):
        '''Set cache for results, update inverted index.'''
        results = response.data
        if self.__is_paginated_response(results):
            # Paginated response
            results = results['results']
        elif isinstance(results, dict):
            # Single object
            results = [results]
        if hasattr(response, 'render') and callable(response.render):
            def set_cache(response):
                cache.set(cache_key, response, self.timeout)
            response.add_post_render_callback(set_cache)
        else:
            cache.set(cache_key, response, self.timeout)

    @classmethod
    def _register_signals(cls):
        signals.m2m_changed.connect(invalidate_all_caches)
        signals.post_save.connect(invalidate_all_caches)
        signals.pre_delete.connect(invalidate_all_caches)
        cls._signals_registered = True

    def dispatch(self, request, *args, **kwargs):
        '''Override dispatch() to check cache.'''
        model_cls = self.get_queryset().model
        app_label = model_cls._meta.app_label
        model_name = model_cls._meta.model_name
        if not self._signals_registered:
            self._register_signals()
        cache_key = build_cache_key(request, app_label, model_name)
        cached_result = cache.get(cache_key, None)
        if cached_result:
            return cached_result
        response = super().dispatch(request, *args, **kwargs)
        if (request.method in ('GET', 'HEAD')
                and self.timeout
                and response.status_code == 200):
            self._build_cache_for_results(cache_key, response)
        return response
