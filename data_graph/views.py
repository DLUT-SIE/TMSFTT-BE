'''Provide API views for data-graph module.'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from data_graph.services import DataGraphService, DataGraphParamsService


class DataGraphView(APIView):
    '''create API views for getting graph data'''

    def get(self, request):
        '''getting data-graph data'''
        request_data = {
            'y_type': request.GET.get('y_type'),
            'x_type': request.GET.get('x_type'),
            'search_start_year': request.GET.get('search_start_year'),
            'search_end_year': request.GET.get('search_end_year'),
            'search_region': request.GET.get('search_region')
        }
        try:
            request_data['y_type'] = int(request_data['y_type'])
            request_data['x_type'] = int(request_data['x_type'])
            request_data['search_start_year'] = int(
                request_data['search_start_year'])
            request_data['search_end_year'] = int(
                request_data['search_end_year'])
        except Exception:
            return Response('参数格式错误', status=status.HTTP_400_BAD_REQUEST)
        DataGraphService.select_sub_service(request_data)
        return Response(request_data, status=status.HTTP_200_OK)


class DataGraphParamView(APIView):
    '''create API views for getting graph all params'''

    def get(self, request):
        '''getting data-graph selection param'''
        data = DataGraphParamsService.get_graph_param()
        return Response(data)
