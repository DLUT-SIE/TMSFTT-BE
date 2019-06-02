'''Define how to serialize our models.'''
from rest_framework import serializers

import training_review.models
from training_review.services import ReviewNoteService


class ReviewNoteSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize ReviewNote instance.'''
    user_name = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = training_review.models.ReviewNote
        fields = '__all__'
        read_only_fields = ('user',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return ReviewNoteService.create_review_note(**validated_data)

    def validate(self, data):
        record = data.get('record')
        if not self.context['request'].user.has_perm(
                'training_record.change_record', record):
            raise serializers.ValidationError('您无权添加审核提示！')
        return data
