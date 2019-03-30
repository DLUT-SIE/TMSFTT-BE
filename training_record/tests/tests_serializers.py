'''Unit tests for training_record serializers.'''
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import serializers

from training_record.serializers import RecordSerializer


# pylint: disable=no-self-use
class TestRecordSerializer(TestCase):
    '''Unit tests for serializer of User.'''
    def test_validate_attachments_data_too_much_attachments(self):
        '''Should raise ValidationError if there are too much attachments.'''
        serializer = RecordSerializer()
        data = [Mock() for _ in range(20)]

        with self.assertRaisesMessage(
                serializers.ValidationError, '最多允许上传3个附件'):
            serializer.validate_attachments_data(data)

    @patch('training_record.serializers.format_file_size',
           return_value='100 MB')
    def test_validate_attachments_data_attachments_too_large(
            self, _):
        '''
        Should raise ValidationError if the size of attachments is too large.
        '''
        serializer = RecordSerializer()
        data = [Mock(size=100*1024*1024) for _ in range(2)]

        with self.assertRaisesMessage(
                serializers.ValidationError,
                '上传附件过大，请修改后再上传。(附件大小: 100 MB)'):
            serializer.validate_attachments_data(data)

    def test_should_return_status_character_correctly(self):
        '''Should return correct status char.'''
        serializer = RecordSerializer()
        data = [Mock(status=i) for i in range(5)]
        self.assertEqual(serializer.get_status_str(data[0]), '未提交')
        self.assertEqual(serializer.get_status_str(data[1]), '已提交')
        self.assertEqual(serializer.get_status_str(data[2]), '院系管理员已审核')
        self.assertEqual(serializer.get_status_str(data[3]), '学校管理员已审核')
        self.assertEqual(serializer.get_status_str(data[4]), '未知状态')
