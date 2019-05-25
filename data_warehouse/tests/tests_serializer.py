'''序列化器测试模块'''
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from data_warehouse.serializers import (
    CoverageStatisticsSerializer,
    TrainingFeedbackSerializer
)


class TestSerializer(TestCase):
    '''序列化器测试'''
    def test_coverage_statistics_serializer(self):
        '''Should 正确的序列化覆盖率统计的前端请求参数'''
        data = {
            'table_type': 1,
            'program_id': '1'
        }
        serializer = CoverageStatisticsSerializer(data=data)
        self.assertEqual(True, serializer.is_valid())
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['program_id'], 1)

        data = {}
        serializer = CoverageStatisticsSerializer(data=data)
        self.assertEqual(False, serializer.is_valid())

        data = {'table_type': 1, 'program_id': 'abc'}
        serializer = CoverageStatisticsSerializer(data=data)
        self.assertEqual(False, serializer.is_valid())

    def test_traning_feedback_serializer(self):
        '''Should 正确的序列化培训反馈的前端请求参数'''
        data = {
            'table_type': '4',
            'program_id': '1'
        }
        serializer = TrainingFeedbackSerializer(data=data)
        self.assertEqual(True, serializer.is_valid(raise_exception=True))
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['program_id'], 1)

        data = {
            'table_type': '4',
        }
        serializer = TrainingFeedbackSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
