'''Provide API views for data-graph module.'''
from rest_framework.response import Response
from rest_framework import status, viewsets

from canvas_data_warehouse.services import CanvasDataService


class CanvasDataViewSet(viewsets.ViewSet):
    '''create API views for getting graph data'''

    def get_canvas_data(self, request):
        '''getting data-graph data'''
        request_data = {
            'y_type': request.GET.get('y_type'),
            'x_type': request.GET.get('x_type'),
            'search_start_year': request.GET.get('search_start_year'),
            'search_end_year': request.GET.get('search_end_year'),
            'search_region': request.GET.get('search_region')
        }
        CanvasDataService.dispatch_sub_service(request_data)
        return Response(request_data, status=status.HTTP_200_OK)


class DataGraphParamViewSet(viewsets.ViewSet):
    '''create API views for getting graph all params'''

    def get_param(self, request):
        '''getting data-graph selection param'''
        data = CanvasDataService.get_graph_param()
        return Response(data)
