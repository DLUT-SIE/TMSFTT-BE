'''Provide API views for training_record module.'''
from rest_framework import viewsets

import training_record.models
import training_record.serializers


class RecordViewSet(viewsets.ModelViewSet):
    '''Create API views for Record.'''
    queryset = training_record.models.Record.objects.all()
    serializer_class = training_record.serializers.RecordSerializer


class RecordContentViewSet(viewsets.ModelViewSet):
    '''Create API views for RecordContent.'''
    queryset = training_record.models.RecordContent.objects.all()
    serializer_class = training_record.serializers.RecordContentSerializer


class RecordAttachmentViewSet(viewsets.ModelViewSet):
    '''Create API views for RecordAttachment.'''
    queryset = training_record.models.RecordAttachment.objects.all()
    serializer_class = training_record.serializers.RecordAttachmentSerializer


class StatusChangeLogViewSet(viewsets.ModelViewSet):
    '''Create API views for StatusChangeLog.'''
    queryset = training_record.models.StatusChangeLog.objects.all()
    serializer_class = training_record.serializers.StatusChangeLogSerializer