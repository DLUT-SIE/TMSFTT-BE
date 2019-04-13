'''Unit tests for training_record models.'''
from unittest.mock import Mock

from django.test import TestCase
from django.utils.timezone import now
from django.utils.text import format_lazy as _f

from training_record.models import (
    Record, RecordContent, RecordAttachment, StatusChangeLog, CampusEventFeedback)


class TestRecord(TestCase):
    '''Unit tests for model Record.'''
    def test_str(self):
        '''Should render string correctly.'''
        user_id = 123

        test_cases = (
            (None, 456),
            (789, None),
        )
        for campus_event_id, off_campus_event_id in test_cases:
            record = Record(
                user_id=user_id,
                campus_event_id=campus_event_id,
                off_campus_event_id=off_campus_event_id,
            )

            expected_str = '{}({})'.format(
                user_id, campus_event_id or off_campus_event_id)

            self.assertEqual(str(record), expected_str)

    def test_check_event_set(self):
        '''
        Should not raise error when only one of campus_event and
        off_campus_event if set, raise error otherwise.
        '''
        test_cases = (
            (None, None),
            (None, 'off campus event'),
            ('campus event', None),
            ('campus event', 'off campus event'),
        )

        for campus_event, off_campus_event in test_cases:
            instance = Mock()
            instance.campus_event = campus_event
            instance.off_campus_event = off_campus_event

            should_raise_error = (
                bool(instance.campus_event) == bool(instance.off_campus_event)
            )
            if should_raise_error:
                # Both campus_event and off_campus_event are set or unset,
                # raise error
                self.assertRaises(ValueError, Record.check_event_set,
                                  None, instance)
            else:
                self.assertIsNone(Record.check_event_set(None, instance))


class TestRecordContent(TestCase):
    '''Unit tests for model RecordContent.'''
    def test_str(self):
        '''Should render string correctly.'''
        record_id = 123
        for content_type, msg in RecordContent.CONTENT_TYPE_CHOICES:
            content = RecordContent(content_type=content_type,
                                    record_id=record_id)

            expected_str = '{}({})'.format(msg, record_id)

            self.assertEqual(str(content), expected_str)


class TestRecordAttachment(TestCase):
    '''Unit tests for model RecordAttachment.'''
    def test_str(self):
        '''Should render string correctly.'''
        record_id = 123
        for attachment_type, msg in RecordAttachment.ATTACHMENT_TYPE_CHOICES:
            attachment = RecordAttachment(attachment_type=attachment_type,
                                          record_id=record_id)
            expected_str = '{}({})'.format(msg, record_id)

            self.assertEqual(str(attachment), expected_str)


class TestStatusChangeLog(TestCase):
    '''Unit tests for model StatusChangeLog.'''
    def test_str(self):
        '''Should render string correctly.'''
        time = now()
        record_id = 123
        for pre_status, pre_msg in Record.STATUS_CHOICES:
            for post_status, post_msg in Record.STATUS_CHOICES:
                expected_str = _f('{}状态于{}由{}变为{}',
                                  record_id, time, pre_msg, post_msg)
                change_log = StatusChangeLog(pre_status=pre_status,
                                             post_status=post_status,
                                             time=time,
                                             record_id=record_id)

                self.assertEqual(str(change_log), str(expected_str))


class TestCampusEventFeedback(TestCase):
    '''Unit tests for model CampusEventFeedback.'''
    def test_str(self):
        '''Should render string correctly.'''
        record_id = 123
        expected_str = '反馈内容({})'.format(record_id)
        campus_event_feedback = CampusEventFeedback(record_id=record_id,
                                                    feedback='')
        self.assertEqual(str(campus_event_feedback), str(expected_str))