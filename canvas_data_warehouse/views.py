'''Provide API views for data-graph module.'''
from rest_framework.response import Response
from rest_framework.decorators import action, list_route
from rest_framework import status, viewsets

from canvas_data_warehouse.services import CanvasDataService


class CanvasDataViewSet(viewsets.ViewSet):
    '''create API views for getting graph data'''
    @list_route(name='get-canvas-data')
    def get_canvas_data(self, request):
        '''getting data-graph data'''
        CanvasDataService.dispatch(request.GET.get('graph_type'), request.GET)
        return Response(request.GET, status=status.HTTP_200_OK)

    @action(detail=False, name='get-params')
    def get_params(self, request):
        '''getting data-graph selection param'''
        data = CanvasDataService.get_graph_param()
        return Response(data)
