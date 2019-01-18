'''Provide API views for training_review module.'''
from rest_framework import viewsets

import training_review.models
import training_review.serializers


class ReviewNoteViewSet(viewsets.ModelViewSet):
    '''Create API views for ReviewNote.'''
    queryset = training_review.models.ReviewNote.objects.all()
    serializer_class = training_review.serializers.ReviewNoteSerializer
