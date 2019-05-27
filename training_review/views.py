'''Provide API views for training_review module.'''
from rest_framework import viewsets, mixins
from rest_framework_guardian import filters
import django_filters

import auth.permissions
import training_review.models
import training_review.serializers
import training_review.filters


class ReviewNoteViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    '''Create API views for ReviewNote.'''
    queryset = (
        training_review.models.ReviewNote.objects.all()
        .select_related('user')
        .order_by('-create_time')
    )
    serializer_class = training_review.serializers.ReviewNoteSerializer
    filter_class = training_review.filters.ReviewNoteFilter
    filter_backends = (filters.DjangoObjectPermissionsFilter,
                       django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (
        auth.permissions.DjangoObjectPermissions,
    )
