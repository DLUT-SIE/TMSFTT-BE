'''Provide API views for data-graph module.'''
import os
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets

from data_warehouse.services.aggregate_data_service import (
    AggregateDataService, CanvasOptionsService
)
from infra.exceptions import BadRequest
from secure_file.models import SecureFile


class AggregateDataViewSet(viewsets.ViewSet):
    '''create API views for getting graph data and table data'''

    @action(detail=False, url_path='data', url_name='data')
    def get_aggregate_data(self, request):
        '''getting data'''
        method_name = request.GET.get('method_name')
        if method_name is None:
            raise BadRequest("错误的参数格式")
        context = {key: val for (key, val) in request.GET.items()}
        context['request'] = request
        canvas_data = AggregateDataService.dispatch(
            method_name, context)
        return Response(canvas_data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='canvas-options', url_name='options')
    def get_canvas_options(self, request):
        '''getting canvas-options'''
        data = CanvasOptionsService.get_canvas_options()
        return Response(data)

    @action(detail=False, methods=['GET'], url_path='table-export',
            url_name='table-export')
    def export(self, request):
        '''Return a xls file stream.'''
        if 'table_type' not in request.GET:
            raise BadRequest('请求的参数不正确。')
        table_type = request.GET['table_type']
        if not table_type.isdigit():
            raise BadRequest('请求的table_type必须为整数。')
        table_type = int(table_type)
        context = {key: val for (key, val) in request.GET.items()}
        context['request'] = request
        ret_file_path, file_name = AggregateDataService.dispatch(
            'table_export', context)
        secure_file = SecureFile.from_path(request.user, file_name,
                                           ret_file_path)
        os.unlink(ret_file_path)
        return secure_file.generate_download_response(request)
