'''Unit tests for training_record utils.'''
from unittest.mock import Mock

from django.test import TestCase

import training_record.models as models
from training_record.utils import (
    infer_attachment_type,
    is_user_allowed_operating,
    is_admin_allowed_operating,
)


class TestInferAttachmentType(TestCase):
    '''Unit tests for infer_attachment_type().'''
    def test_infer_type_content(self):
        '''Should infer attachment_type as CONTENT.'''
        fname = '这是一份培训内容文件.txt'

        attachment_type = infer_attachment_type(fname)

        self.assertEqual(attachment_type,
                         models.RecordAttachment.ATTACHMENT_TYPE_CONTENT)

    def test_infer_type_summary(self):
        '''Should infer attachment_type as SUMMARY.'''
        fname = '这是一份培训总结文件.txt'

        attachment_type = infer_attachment_type(fname)

        self.assertEqual(attachment_type,
                         models.RecordAttachment.ATTACHMENT_TYPE_SUMMARY)

    def test_infer_type_feedkback(self):
        '''Should infer attachment_type as FEEDBACK.'''
        fname = '这是一份培训反馈文件.txt'

        attachment_type = infer_attachment_type(fname)

        self.assertEqual(attachment_type,
                         models.RecordAttachment.ATTACHMENT_TYPE_FEEDBACK)

    def test_infer_type_others(self):
        '''Should infer attachment_type as OTHERS.'''
        fname = '这是一份文件.txt'

        attachment_type = infer_attachment_type(fname)

        self.assertEqual(attachment_type,
                         models.RecordAttachment.ATTACHMENT_TYPE_OTHERS)


class TestIsUserAllowedOperating(TestCase):
    '''Unit tests for is_user_allowed_operating().'''
    def test_user_can_operate(self):
        '''User should be allowed to operate.'''
        user = Mock()
        record = Mock()
        record.user = user
        record.status = models.Record.STATUS_SUBMITTED

        self.assertEqual(is_user_allowed_operating(user, record), True)

    def test_user_can_not_operate(self):
        '''User should not be allowed to operate.'''
        user = Mock()
        record = Mock()
        record.user = user
        record.status = models.Record.STATUS_CLOSED

        self.assertEqual(is_user_allowed_operating(user, record), False)


class TestIsAdminAllowedOperating(TestCase):
    '''Unit tests for is_admin_allowed_operating().'''
    def test_department_admin_can_operate(self):
        '''Department admin should be allowed to operate.'''
        user = Mock()
        user.is_department_admin = True
        user.is_school_admin = False
        record = Mock()
        record.status = models.Record.STATUS_SUBMITTED

        self.assertEqual(
            is_admin_allowed_operating(user, record), True)

    def test_department_admin_can_not_operate(self):
        '''Department admin should not be allowed to operate.'''
        user = Mock()
        user.is_department_admin = True
        user.is_school_admin = False
        record = Mock()
        record.status = models.Record.STATUS_SCHOOL_ADMIN_APPROVED

        self.assertEqual(
            is_admin_allowed_operating(user, record), False)

    def test_school_admin_can_operate(self):
        '''School admin should be allowed to operate.'''
        user = Mock()
        user.is_school_admin = True
        user.is_department_admin = False
        record = Mock()
        record.status = models.Record.STATUS_DEPARTMENT_ADMIN_APPROVED

        self.assertEqual(
            is_admin_allowed_operating(user, record), True)

    def test_school_admin_can_not_operate(self):
        '''School admin should not be allowed to operate.'''
        user = Mock()
        user.is_school_admin = True
        user.is_department_admin = False
        record = Mock()
        record.status = models.Record.STATUS_SUBMITTED

        self.assertEqual(
            is_admin_allowed_operating(user, record), False)
