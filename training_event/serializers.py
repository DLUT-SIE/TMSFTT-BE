'''Define how to serialize our models.'''
from rest_framework import serializers

import training_event.models


class CampusEventSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize CampusEvent instance.'''
    class Meta:
        model = training_event.models.CampusEvent
        fields = '__all__'
        read_only_fields = ('num_enrolled',)


class OffCampusEventSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize OffCampusEvent instance.'''
    class Meta:
        model = training_event.models.OffCampusEvent
        fields = '__all__'


class EnrollmentSerailizer(serializers.ModelSerializer):
    '''Indicate how to serialize Enrollment instance.'''
    class Meta:
        model = training_event.models.Enrollment
        fields = '__all__'
