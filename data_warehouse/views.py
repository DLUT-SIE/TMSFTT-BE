'''Provide API views for data-graph module.'''
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets

from data_warehouse.services.aggregate_data_service import (
    AggregateDataService, CanvasOptionsService
)
from infra.exceptions import BadRequest
from secure_file.models import SecureFile


class AggregateDataViewSet(viewsets.ViewSet):
    '''create API views for getting graph data'''
    TABLE = {
        1: '教职工表',
        2: '专任教师表',
        3: '培训总体情况表',
        4: '专任教师培训覆盖率表',
        5: '培训学时与工作量表'
    }

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
        if 'id' not in request.GET:
            raise BadRequest('请求的参数不正确。')
        method_name = request.GET.get('method_name')
        if method_name is None:
            raise BadRequest("错误的参数格式")
        table_id = request.GET['id']
        target = None
        table_id = int(table_id)
        context = {key: val for (key, val) in request.GET.items()}
        context['request'] = request
        if table_id > 5 or table_id <= 0:
            raise BadRequest('请求的表不存在。')
        if table_id == 1:
            pass
        elif table_id == 2:
            pass
        elif table_id == 3:
            pass
        elif table_id == 4:
            target = AggregateDataService.dispatch(method_name, context)
        elif table_id == 5:
            pass
        f_name = '{}.xls'.format(self.TABLE[table_id])
        secure_file = SecureFile.from_path(request.user, f_name, target)
        return secure_file.generate_download_response(request)
