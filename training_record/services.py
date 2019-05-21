'''Provide services of training record module.'''
import tempfile
import xlrd

from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from auth.services import PermissionService
from infra.exceptions import BadRequest
from training_record.models import (
    Record, RecordContent, RecordAttachment,
    CampusEventFeedback, StatusChangeLog
)
from training_event.models import OffCampusEvent, CampusEvent, EventCoefficient


User = get_user_model()


class RecordService:
    '''Provide services for Record.'''
    @staticmethod
    def create_off_campus_record_from_raw_data(
            off_campus_event=None, user=None,
            contents=None, attachments=None, role=None):
        '''Create a training record of off-campus training event.

        Parameters
        ----------
        off_campus_event: dict
            This dict should have full information needed to create an
            OffCampusEvent.
        user: User
            The user of which the record is related to.
        contents(optional): list of dict
            Every dict of this list should have full information needed to
            create a RecordContent.
        attachments(optional): list of InMemoryFile

        role: number
            The role of the user.

        Returns
        -------
        record: Record
        '''
        if off_campus_event is None:
            raise BadRequest('校外培训活动数据格式无效')
        if user is None or not isinstance(user, User):
            raise BadRequest('用户无效')
        if contents is None:
            contents = []
        if attachments is None:
            attachments = []
        if role not in [
                role for (role, _) in EventCoefficient.ROLE_CHOICES]:
            raise BadRequest('参与方式无效')

        with transaction.atomic():
            off_campus_event = OffCampusEvent.objects.create(
                **off_campus_event,
            )

            event_coefficient = EventCoefficient.objects.create(
                role=role, coefficient=0,
                off_campus_event=off_campus_event)

            record = Record.objects.create(
                off_campus_event=off_campus_event,
                user=user,
                event_coefficient=event_coefficient,
            )
            PermissionService.assign_object_permissions(user, record)

            for content in contents:
                record_content = RecordContent.objects.create(
                    record=record,
                    **content
                )
                PermissionService.assign_object_permissions(
                    user, record_content)

            for attachment in attachments:
                record_attachment = RecordAttachment.objects.create(
                    record=record,
                    path=attachment,
                )
                PermissionService.assign_object_permissions(
                    user, record_attachment)

        return record

    # pylint: disable=invalid-name
    # pylint: disable=redefined-builtin
    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments
    @staticmethod
    def update_off_campus_record_from_raw_data(
            record, off_campus_event=None, user=None,
            contents=None, attachments=None, role=None):
        '''Update the off-campus record

        Parameters
        ----------
        off_campus_event: dict
            This dict should have full information needed to update an
            OffCampusEvent.
        user: User
            The user of which the record is related to.
        contents(optional): list of dict
            Every dict of this list should have full information needed to
            create a RecordContent.
        attachments(optional): list of InMemoryFile

        Returns
        -------
        record: Record
        '''
        off_campus_event_data = off_campus_event
        if off_campus_event_data is None:
            raise BadRequest('校外培训活动数据格式无效')
        if contents is None:
            contents = []
        if attachments is None:
            attachments = []
        if role not in [
                role for (role, _) in EventCoefficient.ROLE_CHOICES]:
            raise BadRequest('参与方式无效')

        with transaction.atomic():
            # get the record to be updated
            try:
                record = Record.objects.select_for_update().get(id=record.id)
            except Exception:
                raise BadRequest('校外培训记录无效')

            # update the offCampusEvent
            try:
                off_campus_event_instance = (
                    OffCampusEvent.objects.select_for_update().get(
                        id=off_campus_event_data.get('id'))
                )
            except Exception:
                raise BadRequest('校外培训活动数据格式无效')

            for key, val in off_campus_event_data.items():
                setattr(off_campus_event_instance, key, val)
            off_campus_event_instance.save()

            record.event_coefficient.role = role
            record.event_coefficient.save()

            # add attachments
            for attachment in attachments:
                record_attachment = RecordAttachment.objects.create(
                    record=record,
                    path=attachment,
                )
                PermissionService.assign_object_permissions(
                    user, record_attachment)

            if RecordAttachment.objects.filter(record=record).count() > 3:
                raise BadRequest('最多允许上传3个附件')

            # Remove all contents and create new, whether
            # they have been changed or not.
            record.contents.all().delete()
            for content in contents:
                record_content = RecordContent.objects.create(
                    record=record,
                    **content
                )
                PermissionService.assign_object_permissions(
                    user, record_content)
        return record

    @staticmethod
    def create_campus_records_from_excel(file):
        '''Create training records of campus training event.

        Parameters
        ----------
        file: InMemoryFile
            This file should have full information needed to create a
            Record of campus-event.
            The first line should be the id of each campus-event.
            For each campus-event, the id of its participant should be
            below its id.

        Returns
        -------
        count of records
        '''

        records = set()

        try:
            # get information
            tup = tempfile.mkstemp()
            with open(tup[0], 'wb') as work_book:
                work_book.write(file)
            # open excel and get the first sheet
            sheet = xlrd.open_workbook(tup[1]).sheet_by_index(0)
        except Exception:
            raise BadRequest('无效的表格')

        with transaction.atomic():
            # get event from sheet
            event_id = int(sheet.cell(0, 0).value)
            try:
                campus_event = CampusEvent.objects.get(pk=event_id)
            except Exception:
                raise BadRequest('编号为{}的活动不存在'.format(event_id))

            # process the info of users
            for index in range(1, sheet.nrows):
                user_id = int(sheet.cell(index, 0).value)

                try:
                    user = User.objects.get(pk=user_id)
                except Exception:
                    raise BadRequest('第{}行，编号为{}的用户不存在'.format(
                        index + 1, user_id))

                event_coefficient_id = int(sheet.cell(index, 1).value)
                try:
                    event_coefficient = EventCoefficient.objects.get(
                        pk=event_coefficient_id)
                except Exception:
                    raise BadRequest('第{}行，编号为{}的活动系数不存在'.format(
                        index + 1, event_coefficient_id))

                record = Record.objects.create(
                    campus_event=campus_event, user=user,
                    status=Record.STATUS_FEEDBACK_REQUIRED,
                    event_coefficient=event_coefficient)
                PermissionService.assign_object_permissions(user, record)
                records.add(record)

        return len(records)

    @staticmethod
    def department_admin_review(record_id, is_approved, user):
        '''Department admin review the off-campus training record.

        This action is atomic, will fail if there is no enough permissions for
        admins to change record status or no such record.

        Parameters
        ----------
        record_id: number
            This parameter represents which record's status should be changed.
        is_approved: Boolean
            This parameter represents whether the record is passed or not.
        user: number
            This parameter represents who reviewed the record.

        Returns
        -------
        record: Record
        '''
        with transaction.atomic():
            record = (Record
                      .objects
                      .select_for_update()
                      .filter(pk=record_id, campus_event__isnull=True))
            if len(record) != 1:
                raise BadRequest('无此培训记录！')
            record = record[0]
            if record.status != Record.STATUS_SUBMITTED:
                raise BadRequest('无权更改！')
            pre_status = record.status
            if is_approved:
                record.status = Record.STATUS_DEPARTMENT_ADMIN_APPROVED
            else:
                record.status = Record.STATUS_DEPARTMENT_ADMIN_REJECTED
            post_status = record.status
            StatusChangeLog.objects.create(
                record=record,
                pre_status=pre_status,
                post_status=post_status,
                time=now(),
                user=user)
            record.save()
        return record

    @staticmethod
    def school_admin_review(record_id, is_approved, user):
        '''School admin review the off-campus training record.

        This action is atomic, will fail if there is no enough permissions for
        admins to change record status or no such record.

        Parameters
        ----------
        record_id: number
            This parameter represents which record's status should be changed.
        is_approved: Boolean
            This parameter represents whether the record is passed or not.
        user: number
            This parameter represents who reviewed the record.

        Returns
        -------
        record: Record
        '''
        with transaction.atomic():
            record = (Record
                      .objects
                      .select_for_update()
                      .filter(pk=record_id, campus_event__isnull=True))
            if len(record) != 1:
                raise BadRequest('无此培训记录！')
            record = record[0]
            if record.status != Record.STATUS_DEPARTMENT_ADMIN_APPROVED:
                raise BadRequest('无权更改！')
            pre_status = record.status
            if is_approved:
                record.status = Record.STATUS_SCHOOL_ADMIN_APPROVED
            else:
                record.status = Record.STATUS_SCHOOL_ADMIN_REJECTED
            post_status = record.status
            StatusChangeLog.objects.create(
                record=record,
                pre_status=pre_status,
                post_status=post_status,
                time=now(),
                user=user)
            record.save()
        return record

    @staticmethod
    def close_record(record_id, user):
        '''School admin close the off-campus training record.

        This action is atomic, will fail if there is no enough permissions for
        admins to close record or no such record.

        Parameters
        ----------
        record_id: number
            This parameter represents which record should be closed.
        user: number
            This parameter represents who closed the record.

        Returns
        -------
        record: Record
        '''
        with transaction.atomic():
            record = (Record
                      .objects
                      .select_for_update()
                      .filter(pk=record_id, campus_event__isnull=True))
            if len(record) != 1:
                raise BadRequest('无此培训记录！')
            record = record[0]
            if ((record.status == Record.STATUS_SCHOOL_ADMIN_APPROVED) |
                    (record.status == Record.STATUS_CLOSED)):
                raise BadRequest('无权更改！')
            pre_status = record.status
            record.status = Record.STATUS_CLOSED
            post_status = record.status
            StatusChangeLog.objects.create(
                record=record,
                pre_status=pre_status,
                post_status=post_status,
                time=now(),
                user=user)
            record.save()
        return record

    @staticmethod
    def get_number_of_records_without_feedback(user):
        '''Get the number of records which requiring feedback'''
        count = Record.objects.filter(
            user=user, off_campus_event__isnull=True, feedback=None).count()
        return count


class CampusEventFeedbackService:
    '''Provide services for CampusEventFeedback.'''
    @staticmethod
    def create_feedback(record, content):
        '''Create feedback for campus-event and update the status
        of the related-record to be STATUS_FEEDBACK_SUBMITTED.'''
        related_record = Record.objects.get(pk=record.id)
        with transaction.atomic():
            feedback = CampusEventFeedback.objects.create(record=record,
                                                          content=content)
            related_record.status = Record.STATUS_FEEDBACK_SUBMITTED
            related_record.save()
        return feedback
