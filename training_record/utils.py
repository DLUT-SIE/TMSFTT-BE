'''Utility functions provided by training_record module.'''
import re


def infer_attachment_type(fname):
    '''Infer attachment_type from file name.'''
    import training_record.models as record_models
    if re.search(r'内容', fname):
        return record_models.RecordAttachment.ATTACHMENT_TYPE_CONTENT
    if re.search(r'总结', fname):
        return record_models.RecordAttachment.ATTACHMENT_TYPE_SUMMARY
    if re.search(r'反馈', fname):
        return record_models.RecordAttachment.ATTACHMENT_TYPE_FEEDBACK
    return record_models.RecordAttachment.ATTACHMENT_TYPE_OTHERS


def is_user_allowed_operating(request, obj):
    '''Check if users can operate.'''
    import training_record.models as record_models
    user_action_status = (
        record_models.Record.STATUS_SUBMITTED,
        record_models.Record.STATUS_DEPARTMENT_ADMIN_REJECTED,
        record_models.Record.STATUS_SCHOOL_ADMIN_REJECTED
    )
    return request.user == obj.user and obj.status in user_action_status


def is_admin_allowed_operating(request, obj):
    '''Check if admin can operate.'''
    import training_record.models as record_models
    department_admin_action_status = (
        record_models.Record.STATUS_SUBMITTED,
        record_models.Record.STATUS_DEPARTMENT_ADMIN_APPROVED,
        record_models.Record.STATUS_DEPARTMENT_ADMIN_REJECTED
    )
    school_admin_action_status = (
        record_models.Record.STATUS_DEPARTMENT_ADMIN_APPROVED,
        record_models.Record.STATUS_SCHOOL_ADMIN_APPROVED,
        record_models.Record.STATUS_SCHOOL_ADMIN_REJECTED
    )
    is_department_admin_allowed = (
        request.user.is_department_admin
        and (obj.status in department_admin_action_status)
    )
    is_school_admin_allowed = (
        request.user.is_school_admin
        and (obj.status in school_admin_action_status)
    )
    return is_department_admin_allowed or is_school_admin_allowed
