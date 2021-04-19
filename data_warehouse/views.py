'''Provide API views for data-graph module.'''
import os
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets, views

from data_warehouse.services.aggregate_data_service import (
    AggregateDataService
)
from data_warehouse.services.canvas_options_service import (
    CanvasOptionsService
)
from data_warehouse.services.log_service import (
    LogService
)
from data_warehouse.serializers import (
    BaseTableExportSerializer
)
from infra.exceptions import BadRequest
from secure_file.models import SecureFile
import auth.permissions


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
        context = {key: val for key, val in request.GET.items()}
        context = self.check_params(context)
        context['request'] = request
        ret_file_path, file_name = AggregateDataService.dispatch(
            'table_export', context)
        secure_file = SecureFile.from_path(request.user, file_name,
                                           ret_file_path)
        os.unlink(ret_file_path)
        return secure_file.generate_download_response(request)

    def check_params(self, params):
        '''根据请求的表格类型去校验http请求参数
        Parameters
        ------
        params: dict
            http params

        Returns
        ------
        dict
            validated params.
        '''
        base_serializer = BaseTableExportSerializer(data=params)
        if not base_serializer.is_valid():
            raise BadRequest('table_type参数不存在或类型不为整数。')
        base_validated_data = base_serializer.validated_data
        table_type = base_validated_data.get('table_type')
        serializer_cls = (
            AggregateDataService.TABLE_SERIALIZERS_CHOICES
            .get(table_type, None)
        )
        # if serializer not found, we just do not touch params
        # except table_type field.
        if serializer_cls is None:
            if params is not None:
                params.update(base_validated_data)
            return params
        serializer = serializer_cls(data=params)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class LogPerformView(views.APIView):
    '''Create API view for get tail of logs.'''

    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )

    def get(self, request, format=None):  # pylint: disable=redefined-builtin
        '''define how to get logs.'''
        n_line = request.GET.get('n_line', 100)
        data = LogService.get_tail_n_logs(int(n_line))
        data.reverse()
        return Response({'results': data}, status=status.HTTP_200_OK)
