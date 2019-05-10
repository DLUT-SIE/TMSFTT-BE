'''Provide API views for data-graph module.'''
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets

from data_warehouse.services import AggregateDataService
from infra.exceptions import BadRequest


class AggregateDataViewSet(viewsets.ViewSet):
    '''create API views for getting graph data'''
    @action(detail=False, url_path='data', url_name='data')
    def get_aggregate_data(self, request):
        '''getting data'''
        method_name = request.GET.get('method_name')
        if method_name is None:
            raise BadRequest("错误的参数格式")
        request_data = {key: val for (key, val) in request.GET.items()}
        context = {'request': request, 'data': request_data}
        canvas_data = AggregateDataService.dispatch(
            method_name, context)
        return Response(canvas_data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='canvas-options', url_name='options')
    def get_canvas_options(self, request):
        '''getting canvas-options'''
        data = AggregateDataService.get_canvas_options()
        return Response(data)
