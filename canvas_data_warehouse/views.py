'''Provide API views for data-graph module.'''
from rest_framework.response import Response
from rest_framework.decorators import action, list_route
from rest_framework import status, viewsets

from canvas_data_warehouse.services import CanvasDataService
from infra.exceptions import BadRequest


class CanvasDataViewSet(viewsets.ViewSet):
    '''create API views for getting graph data'''
    @list_route(url_path='data')
    def get_canvas_data(self, request):
        '''getting canvas-data'''
        graph_type = request.GET.get('graph_type')
        if graph_type is None:
            raise BadRequest("错误的参数格式")
        request_data = {key: val for (key, val) in request.GET.items()}
        canvas_data = CanvasDataService.dispatch(graph_type, request_data)
        return Response(canvas_data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='canvas-options')
    def get_canvas_options(self, request):
        '''getting canvas-options selection param'''
        data = CanvasDataService.get_canvas_options()
        return Response(data)
