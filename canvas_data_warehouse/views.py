'''Provide API views for data-graph module.'''
from rest_framework.response import Response
from rest_framework.decorators import action, list_route
from rest_framework import status, viewsets

from canvas_data_warehouse.services import CanvasDataService


class CanvasDataViewSet(viewsets.ViewSet):
    '''create API views for getting graph data'''
    @list_route(url_path='data')
    def get_canvas_data(self, request):
        '''getting canvas-data'''
        graph_type = request.GET.get('graph_type')
        if graph_type is None:
            return Response("错误的参数格式", status=status.HTTP_400_BAD_REQUEST)
        request_data = {key: val for (key, val) in request.GET.items()}
        CanvasDataService.dispatch(graph_type, request_data)
        return Response(request_data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='options')
    def get_params(self, request):
        '''getting canvas-options selection param'''
        data = CanvasDataService.get_graph_param()
        return Response(data)
