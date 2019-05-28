'''data warehouse序列化器模块'''
from datetime import datetime

import pytz
from rest_framework import serializers
from django.utils.timezone import now

# pylint: disable=W0223


class BaseTableExportSerializer(serializers.Serializer):
    '''表格导出序列化器的基类'''
    table_type = serializers.IntegerField(required=True)


class CoverageStatisticsSerializer(BaseTableExportSerializer):
    '''覆盖率统计用于处理http请求参数的序列化器'''
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    program_id = serializers.IntegerField(required=False)
    department_id = serializers.IntegerField(required=False)


class TrainingFeedbackSerializer(BaseTableExportSerializer):
    '''培训反馈用于处理http请求参数的序列化器'''
    program_id = serializers.IntegerField(required=False)
    department_id = serializers.IntegerField(required=False)

    def validate(self, data):
        '''program_id and department_id can not be None at the same time'''
        if data.get('program_id',
                    None) is None and data.get('department_id', None) is None:
            raise serializers.ValidationError(
                "必须指定program_id或department_id。")
        return data


class SummaryParametersSerializer(serializers.Serializer):
    '''Serialize parameters for school summary and personal summary.'''
    start_time = serializers.DateTimeField(
        required=False, format=None,
        default=lambda: datetime.fromtimestamp(0, pytz.utc))
    end_time = serializers.DateTimeField(
        required=False, format=None,
        default=lambda: now())  # pylint: disable=unnecessary-lambda

    def validate_start_time(self, data):
        '''Round to nearest hour.'''
        return data.replace(minute=0, second=0, microsecond=0)

    def validate_end_time(self, data):
        '''Round to nearest hour.'''
        return data.replace(minute=0, second=0, microsecond=0)

    def validate(self, data):
        '''Validate serializer data.'''
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError('截止时间应晚于起始时间')
        return data


class TrainingHoursSerializer(BaseTableExportSerializer):
    '''培训学时导出用于处理http请求参数的序列化器'''
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)


class TableTrainingRecordsSerializer(BaseTableExportSerializer):
    '''Serialize parameters for training records.'''
    event_name = serializers.CharField(required=False, default='')
    event_location = serializers.CharField(required=False, default='')
    start_time = serializers.DateTimeField(
        required=False, format=None,
        default=lambda: datetime.fromtimestamp(0, pytz.utc))
    end_time = serializers.DateTimeField(
        required=False, format=None,
        default=lambda: now())  # pylint: disable=unnecessary-lambda

    def validate_start_time(self, data):
        '''Round to nearest hour.'''
        return data.replace(minute=0, second=0, microsecond=0)

    def validate_end_time(self, data):
        '''Round to nearest hour.'''
        return data.replace(minute=0, second=0, microsecond=0)

    def validate(self, data):
        '''Validate serializer data.'''
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError('截止时间应晚于起始时间')
        return data
