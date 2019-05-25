'''Provide API views for training_event module.'''
from rest_framework import mixins, viewsets, views, status, decorators
from rest_framework.response import Response
from rest_framework_guardian import filters

from django.contrib.auth import get_user_model
import django_filters

import auth.permissions
from training_event.services import EnrollmentService, CampusEventService
import training_event.models
import training_event.serializers
import training_event.filters

User = get_user_model()


class CampusEventViewSet(viewsets.ModelViewSet):
    '''Create API views for CampusEvent.'''
    queryset = (
        training_event.models.CampusEvent.objects
        .all()
        .select_related('program', 'program__department')
        .order_by('-time')
    )
    serializer_class = training_event.serializers.CampusEventSerializer
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
        round_choices = [
            {
                'type': round_type,
                'name': round_type_name,
            } for round_type, round_type_name in (
                training_event.models.EventCoefficient.ROUND_CHOICES)
        ]
        return Response(round_choices, status=status.HTTP_200_OK)


class RoleChoicesView(views.APIView):
    '''Create API view for get choices of roles.'''
    def get(self, request, format=None):  # pylint: disable=redefined-builtin
        '''define how to get role choices.'''
        role_choices = [
            {
                'role': item[0],
                'role_str': item[1],
            } for item in training_event.models.EventCoefficient.ROLE_CHOICES
        ]
        return Response(role_choices, status=status.HTTP_200_OK)
