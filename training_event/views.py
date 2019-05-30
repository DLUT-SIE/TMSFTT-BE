'''Provide API views for training_event module.'''
import django_filters
from django.core.cache import cache
from rest_framework import mixins, viewsets, views, status, decorators
from rest_framework.response import Response
from rest_framework_guardian import filters

import auth.permissions
from training_event.services import EnrollmentService, CampusEventService
from training_event.models import (
    CampusEvent, OffCampusEvent, Enrollment, EventCoefficient
)
from training_event.serializers import (ReadOnlyCampusEventSerializer,
                                        CampusEventSerializer,
                                        OffCampusEventSerializer,
                                        EnrollmentSerailizer)
import training_event.serializers
import training_event.filters
from infra.mixins import MultiSerializerActionClassMixin
from drf_cache.mixins import DRFCacheMixin


class CampusEventViewSet(DRFCacheMixin,
                         MultiSerializerActionClassMixin,
                         viewsets.ModelViewSet):
    '''Create API views for CampusEvent.'''
    queryset = (
        CampusEvent.objects
        .all()
        .select_related('program', 'program__department')
        .prefetch_related('coefficients')
        .order_by('-time')
    )
    serializer_action_classes = {
        'create': CampusEventSerializer,
        'update': CampusEventSerializer,
        'delete': CampusEventSerializer,
        'partial_update': CampusEventSerializer,
    }
    serializer_class = ReadOnlyCampusEventSerializer
    filter_class = training_event.filters.CampusEventFilter
    filter_backends = (filters.DjangoObjectPermissionsFilter,
                       django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (
        auth.permissions.DjangoObjectPermissions,
    )
    perms_map = {
        'review_event': ['%(app_label)s.review_%(model_name)s'],
    }

    @decorators.action(methods=['POST'], detail=True,
                       url_path='review-event')
    def review_event(self, request, pk=None):  # pylint: disable=invalid-name
        '''Review campus event, mark reviewed as True.'''
        event = self.get_object()
        CampusEventService.review_campus_event(event, request.user)
        return Response(status=status.HTTP_201_CREATED)


class OffCampusEventViewSet(DRFCacheMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    '''Create API views for OffCampusEvent.'''
    queryset = OffCampusEvent.objects.all()
    serializer_class = OffCampusEventSerializer
    filter_class = training_event.filters.OffCampusEventFilter


class EnrollmentViewSet(DRFCacheMixin,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    '''Create API views for Enrollment.

    It allows users to create, list, retrieve, destroy their enrollments,
    but do not allow them to update.
    '''
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerailizer
    permission_classes = (
        auth.permissions.DjangoObjectPermissions,
    )

    def perform_destroy(self, instance):
        '''Use service to change num_enrolled and delete enrollment.'''
        EnrollmentService.delete_enrollment(instance)


class RoundChoicesView(views.APIView):
    '''Create API view for get round choices of event coefficient.'''
    def get(self, request, format=None):  # pylint: disable=redefined-builtin
        '''define how to get round choices.'''
        cache_key = 'round-choices'
        round_choices = cache.get(cache_key)
        if round_choices is None:
            round_choices = [
                {
                    'type': round_type,
                    'name': name,
                } for round_type, name in EventCoefficient.ROUND_CHOICES
            ]
            cache.set(cache_key, round_choices, 10 * 60)
        return Response(round_choices, status=status.HTTP_200_OK)


class RoleChoicesView(views.APIView):
    '''Create API view for get choices of roles.'''
    def get(self, request, format=None):  # pylint: disable=redefined-builtin
        '''define how to get role choices.'''
        cache_key = 'role-choices'
        role_choices = cache.get(cache_key)
        if role_choices is None:
            role_choices = [
                {
                    'role': role,
                    'role_str': role_str,
                } for role, role_str in EventCoefficient.ROLE_CHOICES
            ]
            cache.set(cache_key, role_choices, 10 * 60)
        return Response(role_choices, status=status.HTTP_200_OK)
