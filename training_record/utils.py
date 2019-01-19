'''Utility functions provided by training_record module.'''
import re

import training_record.models as record_models


def infer_attachment_type(fname):
    '''Infer attachment_type from file name.'''
    if re.search(r'内容', fname):
        return record_models.RecordAttachment.ATTACHMENT_TYPE_CONTENT
    if re.search(r'总结', fname):
        return record_models.RecordAttachment.ATTACHMENT_TYPE_SUMMARY
    if re.search(r'反馈', fname):
        return record_models.RecordAttachment.ATTACHMENT_TYPE_FEEDBACK
    return record_models.RecordAttachment.ATTACHMENT_TYPE_OTHERS
