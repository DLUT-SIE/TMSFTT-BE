'''Provide API views for training_event module.'''
from rest_framework import mixins, viewsets

import training_event.models
import training_event.serializers
import training_event.filters


class CampusEventViewSet(viewsets.ModelViewSet):
    '''Create API views for CampusEvent.'''
    queryset = training_event.models.CampusEvent.objects.all().order_by(
        '-time')
    serializer_class = training_event.serializers.CampusEventSerializer


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
