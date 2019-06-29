'''Provide API views for training_record module.'''
import django_filters
from django.db.models import Q
from rest_framework import viewsets, status, decorators, mixins
from rest_framework.response import Response
from rest_framework_guardian import filters

import auth.permissions
from auth.models import User
import training_record.models
import training_record.filters
from training_record.models import Record
from training_record.utils import (
    get_department_admin_actionable_status,
    get_school_admin_actionable_status,
)
from training_record.services import RecordService
from training_record.serializers import (CampusEventFeedbackSerializer,
                                         RecordWriteSerializer,
                                         ReadOnlyRecordSerializer)
from training_event.serializers import CampusEventSerializer
from infra.mixins import MultiSerializerActionClassMixin
from infra.exceptions import BadRequest
from drf_cache.mixins import DRFCacheMixin


# pylint: disable=C0103
class RecordViewSet(DRFCacheMixin,
                    MultiSerializerActionClassMixin,
                    viewsets.ModelViewSet):
    '''Create API views for Record.'''
    queryset = (
        training_record.models.Record.objects.all()
        .select_related('campus_event__program__department')
        .select_related('off_campus_event')
        .select_related('event_coefficient')
        .select_related('feedback')
        .prefetch_related('contents', 'attachments')
        .extra(select={
            'is_status_feedback_required':
            f'status={Record.STATUS_FEEDBACK_REQUIRED}'})
        .order_by('-is_status_feedback_required', '-create_time')
    )
    filter_class = training_record.filters.RecordFilter
    serializer_action_classes = {
        'create': RecordWriteSerializer,
        'partial_update': RecordWriteSerializer,
        'update': RecordWriteSerializer,
    }
    serializer_class = ReadOnlyRecordSerializer
    perms_map = {
        'reviewed': ['%(app_label)s.view_%(model_name)s'],
        'department_admin_review': ['%(app_label)s.review_%(model_name)s'],
        'school_admin_review': ['%(app_label)s.review_%(model_name)s'],
        'close_record': ['%(app_label)s.change_%(model_name)s'],
        'force_close_record': ['%(app_label)s.change_%(model_name)s'],
        'batch_submit': ['%(app_label)s.batchadd_%(model_name)s'],
        'get_number_of_records_without_feedback':
            ['%(app_label)s.view_%(model_name)s'],
        'get_role_choices': ['%(app_label)s.view_%(model_name)s'],
        'list_records_for_review': ['%(app_label)s.view_%(model_name)s'],
        'list_records_by_event': ['%(app_label)s.view_%(model_name)s'],
        'get_recent_events': ['%(app_label)s.view_%(model_name)s'],
    }
    filter_backends = (filters.DjangoObjectPermissionsFilter,
                       django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (
        auth.permissions.DjangoObjectPermissions,
    )

    def _get_paginated_response(self, queryset):
        '''Return paginated response'''
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request):

        username = request.query_params.get('user__username', None)
        if username is None or username == '':
            user = request.user
        else:
            user = User.objects.filter(username=username).first()
            if user and not (request.user.is_school_admin or (
                    request.user.check_department_admin(
                        user.department))):
                raise BadRequest('您无权查看该用户的培训记录')

        queryset = self.filter_queryset(self.get_queryset()).filter(
            user=user)
        return self._get_paginated_response(queryset)

    @decorators.action(detail=False, methods=['GET'],
                       url_path='list-records-by-event')
    def list_records_by_event(self, request):
        '''Return records in certain campus_event.'''
        campus_event = request.query_params.get('campus_event')
        if not (request.user.is_school_admin or (
                request.user.check_department_admin(
                    campus_event.program.department))):
            raise BadRequest('您无权查看该活动下的培训记录')

        queryset = self.filter_queryset(self.get_queryset()).filter(
            campus_event=campus_event, off_campus_event__isnull=True,
        )
        return self._get_paginated_response(queryset)

    @decorators.action(detail=False, methods=['GET'],
                       url_path='list-records-for-review')
    def list_records_for_review(self, request):
        '''Return all offCampusRecords for admin'''
        queryset = (
            self.filter_queryset(self.get_queryset())
            .filter(off_campus_event__isnull=False)
        )
        if request.user.is_department_admin:
            queryset = queryset.filter(
                status__in=get_department_admin_actionable_status(),
            )
            queryset = queryset.extra(select={
                'is_status_submitted':
                f'status={Record.STATUS_SUBMITTED}',
                'is_status_department_admin_rejected':
                f'status={Record.STATUS_DEPARTMENT_ADMIN_REJECTED}',
                'is_status_department_admin_approved':
                f'status={Record.STATUS_DEPARTMENT_ADMIN_APPROVED}'
                }).order_by(
                    '-is_status_submitted',
                    '-is_status_department_admin_rejected',
                    '-is_status_department_admin_approved',
                    '-create_time')
            return self._get_paginated_response(queryset)
        queryset = queryset.filter(
            status__in=get_school_admin_actionable_status(),
        )
        queryset = queryset.extra(select={
            'is_status_department_admin_approved':
            f'status={Record.STATUS_DEPARTMENT_ADMIN_APPROVED}',
            'is_status_school_admin_rejected':
            f'status={Record.STATUS_SCHOOL_ADMIN_REJECTED}',
            'is_status_school_admin_approved':
            f'status={Record.STATUS_SCHOOL_ADMIN_APPROVED}'
            }).order_by(
                '-is_status_department_admin_approved',
                '-is_status_school_admin_rejected',
                '-is_status_school_admin_approved',
                '-create_time')
        return self._get_paginated_response(queryset)

    @decorators.action(detail=False, methods=['GET'], url_path='reviewed')
    def reviewed(self, request):
        '''Return records which are already reviewed.'''
        queryset = self.filter_queryset(self.get_queryset()).filter(
            Q(user=request.user),
            Q(status=training_record.models.Record
              .STATUS_SCHOOL_ADMIN_APPROVED) |
            Q(campus_event__isnull=False),
        )
        return self._get_paginated_response(queryset)

    @decorators.action(detail=True, methods=['POST'],
                       url_path='department-admin-review')
    def department_admin_review(self, request, pk):
        '''Pass the record which is being reviewed.'''
        is_approved = request.data.get('isApproved')
        RecordService.department_admin_review(pk,
                                              is_approved,
                                              request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=['POST'],
                       url_path='school-admin-review')
    def school_admin_review(self, request, pk):
        '''Pass the record which is being reviewed.'''
        is_approved = request.data.get('isApproved')
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
                       url_path='force-close')
    def force_close_record(self, request):
        '''Close the record which should not be changed any more.'''
        campus_event = request.data.get('campus_event')
        user = request.data.get('user_id')
        try:
            record = Record.objects.get(campus_event=campus_event,
                                        user=user)
        except Exception:
            raise BadRequest('要关闭的记录不存在')
        RecordService.close_record(record.id,
                                   request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, methods=['POST'],
                       url_path='batch-submit')
    def batch_submit(self, request):
        '''Return count of records which are created.'''
        excel = request.FILES.get('file').read()
        context = {
            'user': request.user,
        }
        count = RecordService.create_campus_records_from_excel(
            excel, context)
        return Response({'count': count}, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=['GET'],
                       url_path='no-feedback-records-count')
    def get_number_of_records_without_feedback(self, request):
        '''Return count of records which requiring feedback'''
        count = RecordService.get_number_of_records_without_feedback(
            request.user)
        return Response({'count': count}, status=status.HTTP_200_OK)

    @decorators.action(detail=False, methods=['GET'],
                       url_path='recent-events')
    def get_recent_events(self, request):
        '''Get the recent events which has records.'''
        events = RecordService.get_recent_events_of_import_records()
        data = CampusEventSerializer(events, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class RecordContentViewSet(DRFCacheMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    '''Create API views for RecordContent.'''
    queryset = training_record.models.RecordContent.objects.all()
    serializer_class = training_record.serializers.RecordContentSerializer
    filter_class = training_record.filters.RecordContentFilter
    filter_backends = (filters.DjangoObjectPermissionsFilter,
                       django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (
        auth.permissions.DjangoObjectPermissions,
    )


class RecordAttachmentViewSet(DRFCacheMixin,
                              mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    '''Create API views for RecordAttachment.'''
    queryset = training_record.models.RecordAttachment.objects.all()
    serializer_class = training_record.serializers.RecordAttachmentSerializer
    filter_class = training_record.filters.RecordAttachmentFilter
    filter_backends = (filters.DjangoObjectPermissionsFilter,
                       django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (
        auth.permissions.DjangoObjectPermissions,
    )


class StatusChangeLogViewSet(DRFCacheMixin,
                             viewsets.ReadOnlyModelViewSet):
    '''Create API views for StatusChangeLog.'''
    queryset = (
        training_record.models.StatusChangeLog.objects.all()
        .select_related('user')
        .order_by('-time')
    )
    serializer_class = training_record.serializers.StatusChangeLogSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('record',)


class CampusEventFeedbackViewSet(DRFCacheMixin,
                                 mixins.CreateModelMixin,
                                 viewsets.GenericViewSet):
    '''Create API views for CampusEventFeedback.'''
    queryset = training_record.models.CampusEventFeedback.objects.all()
    serializer_class = CampusEventFeedbackSerializer
    permission_classes = (
        auth.permissions.DjangoModelPermissions,
    )
