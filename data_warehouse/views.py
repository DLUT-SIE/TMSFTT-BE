'''Provide API views for data-graph module.'''
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets

from data_warehouse.services import AggregateDataService
from infra.exceptions import BadRequest


class AggregateDataViewSet(viewsets.ViewSet):
    '''create API views for getting graph data'''
    @action(detail=False, url_path='data')
    def get_aggregate_data(self, request):
        '''getting canvas-data'''
        graph_type = request.GET.get('graph_type')
        if graph_type is None:
            raise BadRequest("错误的参数格式")
        request_data = {key: val for (key, val) in request.GET.items()}
        canvas_data = AggregateDataService.dispatch(
            request, graph_type, request_data)
        return Response(canvas_data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='canvas-options')
    def get_canvas_options(self, request):
        '''getting canvas-options selection param'''
        data = AggregateDataService.get_canvas_options()
        return Response(data)
