'''data warehouse序列化器模块'''
from rest_framework import serializers

# pylint: disable=W0223


class BaseTableExportSerializer(serializers.Serializer):
    '''序列化器的基类'''
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
            raise serializers.ValidationError("必须指定program_id或department_id。")
        return data
