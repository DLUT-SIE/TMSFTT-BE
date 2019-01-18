'''Define how to serialize our models.'''
from rest_framework import serializers

import training_review.models


class ReviewNoteSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize ReviewNote instance.'''
    class Meta:
        model = training_review.models.ReviewNote
        fields = '__all__'
