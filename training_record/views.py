'''Provide API views for training_record module.'''
from django.db.models import Q
from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework_bulk.mixins import (
    BulkCreateModelMixin,
)

import auth.permissions
import training_record.models
import training_record.filters
from training_record.models import Record
from training_record.services import RecordService
from training_record.serializers import (CampusEventFeedbackSerializer,
                                         RecordCreateSerializer,
                                         ReadOnlyRecordSerializer)
from infra.mixins import MultiSerializerActionClassMixin
from training_event.models import EventCoefficient


# pylint: disable=C0103
class RecordViewSet(MultiSerializerActionClassMixin,
                    viewsets.ModelViewSet):
    '''Create API views for Record.'''
    queryset = (
        training_record.models.Record.objects.all()
        .select_related('feedback', 'campus_event', 'off_campus_event')
        .extra(select={
            'is_status_feedback_required':
            f'status={Record.STATUS_FEEDBACK_REQUIRED}'})
        .order_by('-is_status_feedback_required', '-create_time')
    )
    filter_class = training_record.filters.RecordFilter
    serializer_action_classes = {
        'create': RecordCreateSerializer,
        'partial_update': RecordCreateSerializer,
        'update': RecordCreateSerializer,
    }
    serializer_class = ReadOnlyRecordSerializer
    perms_map = {
        'reviewed': ['%(app_label)s.view_%(model_name)s'],
        'department_admin_review': ['%(app_label)s.review_%(model_name)s'],
        'school_admin_review': ['%(app_label)s.review_%(model_name)s'],
        'close_record': ['%(app_label)s.update_%(model_name)s'],
        'batch_submit': ['%(app_label)s.update_%(model_name)s'],
        'get_number_of_records_without_feedback':
            ['%(app_label)s.view_%(model_name)s'],
    }

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

    @decorators.action(detail=True, methods=['POST'],
                       url_path='close')
    def close_record(self, request, pk):
        '''Close the record which should not be changed any more.'''
        RecordService.close_record(pk,
                                   request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, methods=['POST'],
                       url_path='batch-submit')
    def batch_submit(self, request):
        '''Return count of records which are created.'''
        excel = request.FILES.get('file').read()
        count = RecordService.create_campus_records_from_excel(excel)
        return Response({'count': count}, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=['GET'],
                       url_path='no-feedback-records-count')
    def get_number_of_records_without_feedback(self, request):
        '''Return count of records which requiring feedback'''
        count = RecordService.get_number_of_records_without_feedback(
            request.user)
        return Response({'count': count}, status=status.HTTP_200_OK)

    @decorators.action(detail=False, methods=['GET'],
                       url_path='role-choices')
    def get_role_choices(self, request):
        '''Get role choices in event_coefficient'''
        role_choices = [
            {
                'role': item[0],
                'role_str': item[1],
            } for item in EventCoefficient.ROLE_CHOICES
        ]
        return Response(role_choices, status=status.HTTP_200_OK)


class RecordContentViewSet(BulkCreateModelMixin, viewsets.ModelViewSet):
    '''Create API views for RecordContent.'''
    queryset = training_record.models.RecordContent.objects.all()
    serializer_class = training_record.serializers.RecordContentSerializer
    filter_class = training_record.filters.RecordContentFilter


class RecordAttachmentViewSet(BulkCreateModelMixin, viewsets.ModelViewSet):
    '''Create API views for RecordAttachment.'''
    queryset = training_record.models.RecordAttachment.objects.all()
    serializer_class = training_record.serializers.RecordAttachmentSerializer
    filter_class = training_record.filters.RecordAttachmentFilter


class StatusChangeLogViewSet(viewsets.ModelViewSet):
    '''Create API views for StatusChangeLog.'''
    queryset = training_record.models.StatusChangeLog.objects.all()
    serializer_class = training_record.serializers.StatusChangeLogSerializer


class CampusEventFeedbackViewSet(viewsets.ModelViewSet):
    '''Create API views for CampusEventFeedback.'''
    queryset = training_record.models.CampusEventFeedback.objects.all()
    serializer_class = CampusEventFeedbackSerializer
    permission_classes = (
        auth.permissions.DjangoModelPermissions,
    )
