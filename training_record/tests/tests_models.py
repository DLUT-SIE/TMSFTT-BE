from unittest.mock import patch, Mock

from django.test import TestCase
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from training_record.models import (
    Record, RecordContent, RecordAttachment, StatusChangeLog)


class TestRecord(TestCase):
    @patch('training_record.models.Record.program')
    @patch('training_record.models.Record.user')
    def test_str(self, mocked_user, mocked_program):
        user = 'user'
        mocked_user.__str__.return_value = user

        test_cases = (
            (None, 'program not in system'),
            ('program in system', None),
        )
        for program, program_name in test_cases:
            if program:
                mocked_program.__bool__.return_value = True
                mocked_program.__str__.return_value = program
            else:
                mocked_program.__bool__.return_value = False
            expected_str = '{}({})'.format(user, program or program_name)

            record = Record(program_name=program_name)

            self.assertEqual(str(record), expected_str)

    def test_check_program_set(self):
        test_cases = (
            (None, None),
            (None, 'program not in system'),
            ('program in system', None),
            ('program in system', 'program not in system'),
        )

        for program, program_name in test_cases:
            instance = Mock()
            instance.program_name = program_name
            instance.program = program

            if (program and program_name) or not (program or program_name):
                # Both program and program_name are set or unset, raise error
                self.assertRaises(ValueError, Record.check_program_set,
                                  None, instance)
            else:
                self.assertIsNone(Record.check_program_set(None, instance))


class TestRecordContent(TestCase):
    @patch('training_record.models.RecordContent.record')
    def test_str(self, mocked_record):
        record = 'record'
        mocked_record.__str__.return_value = record
        for type, msg in RecordContent.CONTENT_TYPE_CHOICES:
            content = RecordContent(content_type=type)
            expected_str = '{}({})'.format(msg, record)

            self.assertEqual(str(content), expected_str)


class TestRecordAttachment(TestCase):
    @patch('training_record.models.RecordAttachment.record')
    def test_str(self, mocked_record):
        record = 'record'
        mocked_record.__str__.return_value = record
        for type, msg in RecordAttachment.ATTACHMENT_TYPE_CHOICES:
            attachment = RecordAttachment(attachment_type=type)
            expected_str = '{}({})'.format(msg, record)

            self.assertEqual(str(attachment), expected_str)


class TestStatusChangeLog(TestCase):
    @patch('training_record.models.StatusChangeLog.record')
    def test_str(self, mocked_record):
        record = 'record'
        time = now()
        mocked_record.__str__.return_value = record
        for pre_status, pre_msg in Record.STATUS_CHOICES:
            for post_status, post_msg in Record.STATUS_CHOICES:
                expected_str = _('{}状态于{}由{}变为{}').format(
                    record, time, pre_msg, post_msg)
                change_log = StatusChangeLog(pre_status=pre_status,
                                             post_status=post_status,
                                             time=time)

                self.assertEqual(str(change_log), expected_str)
