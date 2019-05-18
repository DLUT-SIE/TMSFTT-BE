'''Define how to serialize our models.'''
from rest_framework import serializers

import training_review.models
from training_review.services import ReviewNoteService


class ReviewNoteSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize ReviewNote instance.'''
    class Meta:
        model = training_review.models.ReviewNote
        fields = '__all__'

    def create(self, validated_data):
        return ReviewNoteService.create_review_note(validated_data)
