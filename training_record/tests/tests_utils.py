'''Unit tests for training_record utils.'''
from django.test import TestCase

import training_record.models as models
from training_record.utils import (
    infer_attachment_type,
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
