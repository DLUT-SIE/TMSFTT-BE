'''Unit tests for training_record serializers.'''
from django.contrib.auth import get_user_model
from django.test import TestCase

import training_record.serializers as serializers
import training_record.models as models


User = get_user_model()


class TestUserSerializer(TestCase):
    '''Unit tests for serializer of User.'''
    def test_fields_equal(self):
        '''Serializer should return fields of User correctly.'''
        user = User()
        expected_keys = {
            'id', 'last_login', 'first_name', 'last_name', 'email',
            'is_active', 'date_joined'}

        keys = set(serializers.UserSerializer(user).data.keys())
        self.assertEqual(keys, expected_keys)


class TestRecordSerializer(TestCase):
    '''Unit tests for serializer of Record.'''
    def test_fields_equal(self):
        '''Serializer should return fields of Record correctly.'''
        record = models.Record()
        expected_keys = {'id', 'create_time', 'update_time', 'campus_event ', 
                        'off_campus_event','user','status'}

        keys = set(serializers.RecordSerializer(record).data.keys())
        self.assertEqual(keys, expected_keys)


class TestRecordContentSerializer(TestCase):
    '''Unit tests for serializer of RecordContent.'''
    def test_fields_equal(self):
        '''Serializer should return fields of RecordContent correctly.'''
        recordcontent = models.RecordContent()
        expected_keys = {'id', 'create_time', 'update_time', 'record', 
                        'content_type','content'}

        keys = set(serializers.RecordContentSerializer(recordcontent).data.keys())
        self.assertEqual(keys, expected_keys)


class TestRecordAttachmentSerializer(TestCase):
    '''Unit tests for serializer of RecordAttachment.'''
    def test_fields_equal(self):
        '''Serializer should return fields of RecordAttachment correctly.'''
        recordattachment = models.RecordAttachment()
        expected_keys = {'id', 'create_time', 'update_time', 'record', 
                        'attachment_type','path'}

        keys = set(serializers.RecordAttachmentSerializer(recordattachment).data.keys())
        self.assertEqual(keys, expected_keys)


class StatusChangeLogSerializer(TestCase):
    '''Unit tests for serializer of StatusChangeLog.'''
    def test_fields_equal(self):
        '''Serializer should return fields of StatusChangeLog correctly.'''
        statuschangelog = models.StatusChangeLog()
        expected_keys = {'id', 'record', 'pre_status', 'post_status', 'time', 'user'}

        keys = set(serializers.StatusChangeLogSerializer(statuschangelog).data.keys())
        self.assertEqual(keys, expected_keys)