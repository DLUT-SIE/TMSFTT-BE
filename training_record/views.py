'''Provide API views for training_record module.'''
from django.db.models import Q
from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework_bulk.mixins import (
    BulkCreateModelMixin,
)

import training_record.models
import training_record.filters
from training_record.services import RecordService
from training_record.serializers import (CampusEventFeedbackSerializer,
                                         RecordCreateSerializer,
                                         ReadOnlyRecordSerializer)
from infra.mixins import MultiSerializerActionClassMixin


# pylint: disable=C0103
class RecordViewSet(MultiSerializerActionClassMixin,
                    viewsets.ModelViewSet):
    '''Create API views for Record.'''
    queryset = (
        training_record.models.Record.objects.all()
        .select_related('feedback', 'campus_event', 'off_campus_event')
    )
    filter_class = training_record.filters.RecordFilter
    serializer_action_classes = {
        'create': RecordCreateSerializer,
        'partial_update': RecordCreateSerializer,
        'update': RecordCreateSerializer,
    }
    serializer_class = ReadOnlyRecordSerializer

# TODO: rename this action
    def _get_reviewed_status_filtered_records(self, request, is_reviewed):
        '''Return filtered records based on status.'''
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(
            Q(status=training_record.models.Record
              .STATUS_SCHOOL_ADMIN_APPROVED) |
            Q(campus_event__isnull=False))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['GET'], url_path='reviewed')
    def reviewed(self, request):
        '''Return records which are already reviewed.'''
        return self._get_reviewed_status_filtered_records(request, True)

    @decorators.action(detail=True, methods=['POST'],
                       url_path='department-admin-review')
    def department_admin_review(self, request, pk):
        '''Pass the record which is being reviewed.'''
        is_approved = request.data.get('is_approved')
        RecordService.department_admin_review(pk,
                                              is_approved,
                                              request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=['POST'],
                       url_path='school-admin-review')
    def school_admin_review(self, request, pk):
        '''Pass the record which is being reviewed.'''
        is_approved = request.data.get('is_approved')
        RecordService.school_admin_review(pk,
                                          is_approved,
                                          request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, methods=['POST'],
                       url_path='batch-submit')
    def batch_submit(self, request):
        '''Return count of records which are created.'''
        excel = request.FILES.get('file').read()
        count = RecordService.create_campus_records_from_excel(excel)
        return Response({'count': count}, status=status.HTTP_201_CREATED)


class RecordContentViewSet(BulkCreateModelMixin, viewsets.ModelViewSet):
    '''Create API views for RecordContent.'''
    queryset = training_record.models.RecordContent.objects.all()
    serializer_class = training_record.serializers.RecordContentSerializer


class RecordAttachmentViewSet(BulkCreateModelMixin, viewsets.ModelViewSet):
    '''Create API views for RecordAttachment.'''
    queryset = training_record.models.RecordAttachment.objects.all()
    serializer_class = training_record.serializers.RecordAttachmentSerializer


class StatusChangeLogViewSet(viewsets.ModelViewSet):
    '''Create API views for StatusChangeLog.'''
    queryset = training_record.models.StatusChangeLog.objects.all()
    serializer_class = training_record.serializers.StatusChangeLogSerializer


class CampusEventFeedbackViewSet(viewsets.ModelViewSet):
    '''Create API views for CampusEventFeedback.'''
    queryset = training_record.models.CampusEventFeedback.objects.all()
    serializer_class = CampusEventFeedbackSerializer
