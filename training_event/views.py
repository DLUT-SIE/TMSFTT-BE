'''Provide API views for training_event module.'''
import os
from rest_framework import mixins, viewsets
from rest_framework.views import APIView
from django.utils.timezone import now

import training_event.models
import training_event.serializers
import training_event.filters
from training_event.services import CoefficientCalculationService
from secure_file.models import SecureFile


class CampusEventViewSet(viewsets.ModelViewSet):
    '''Create API views for CampusEvent.'''
    queryset = training_event.models.CampusEvent.objects.all().order_by(
        '-time')
    serializer_class = training_event.serializers.CampusEventSerializer
    filter_class = training_event.filters.CampusEventFilter


class OffCampusEventViewSet(viewsets.ModelViewSet):
    '''Create API views for OffCampusEvent.'''
    queryset = training_event.models.OffCampusEvent.objects.all()
    serializer_class = training_event.serializers.OffCampusEventSerializer
    filter_class = training_event.filters.OffCampusEventFilter


class EnrollmentViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    '''Create API views for Enrollment.

    It allows users to create, list, retrieve, destroy their enrollments,
    but do not allow them to update.
    '''
    queryset = training_event.models.Enrollment.objects.all()
    serializer_class = training_event.serializers.EnrollmentSerailizer


class WorkloadFileDownloadView(APIView):
    '''Create API views for downloading workload file'''

    FILE_NAME_TEMPLATE = '{}至{}教师工作量导出表.xls'

    def post(self, request):
        '''get workload file by coefficient service'''

        # 生成excel文件
        user = request.user
        data = request.data
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if end_time is None:
            end_time = now()
        if start_time is None:
            start_time = end_time.replace(year=end_time.year - 1,
                                          month=12, day=31, hour=16, minute=0,
                                          second=0)

        workload_dict = (
            CoefficientCalculationService.calculate_workload_by_query(
                department=data.get('department'),
                start_time=start_time,
                end_time=end_time,
                teachers=data.get('teachers')
            )
        )
        file_path = (
            CoefficientCalculationService.generate_workload_excel_from_data(
                workload_dict=workload_dict
            )
        )

        # 拼接文件名
        file_name = self.FILE_NAME_TEMPLATE.format(
            start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d'))
        secure_file = SecureFile.from_path(user, file_name, file_path)
        os.unlink(file_path)

        return secure_file.generate_secured_download_response(request)
