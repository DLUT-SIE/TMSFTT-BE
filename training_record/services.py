'''Provide services of training record module.'''
import tempfile
import xlrd

from django.db import transaction
from django.contrib.auth import get_user_model

from infra.exceptions import BadRequest
from training_record.models import (
    Record, RecordContent, RecordAttachment, CampusEventFeedback,
)
from training_event.models import OffCampusEvent, CampusEvent, EventCoefficient


User = get_user_model()


class RecordService:
    '''Provide services for Record.'''
    @staticmethod
    def create_off_campus_record_from_raw_data(
            off_campus_event_data=None, user=None,
            contents_data=None, attachments_data=None, event_coefficient=None):
        '''Create a training record of off-campus training event.

        Parameters
        ----------
        off_campus_event_data: dict
            This dict should have full information needed to create an
            OffCampusEvent.
        user: User
            The user of which the record is related to.
        contents_data(optional): list of dict
            Every dict of this list should have full information needed to
            create a RecordContent.
        attachments_data(optional): list of InMemoryFile

        Returns
        -------
        record: Record
        '''
        if off_campus_event_data is None:
            raise BadRequest('校外培训活动数据格式无效')
        if user is None or not isinstance(user, User):
            raise BadRequest('用户无效')
        if contents_data is None:
            contents_data = []
        if attachments_data is None:
            attachments_data = []

        with transaction.atomic():
            off_campus_event = OffCampusEvent.objects.create(
                **off_campus_event_data,
            )

            if event_coefficient is None:
                event_coefficient = EventCoefficient.objects.create(
                    role=EventCoefficient.ROLE_PARTICIPATOR, coefficient=0,
                    hours_option=EventCoefficient.ROUND_METHOD_NONE,
                    workload_option=EventCoefficient.ROUND_METHOD_NONE,
                    off_campus_event=off_campus_event)

            record = Record.objects.create(
                off_campus_event=off_campus_event,
                user=user,
                event_coefficient=event_coefficient,
            )

            for content_data in contents_data:
                RecordContent.objects.create(
                    record=record,
                    **content_data
                )

            for attachment in attachments_data:
                RecordAttachment.objects.create(
                    record=record,
                    path=attachment,
                )
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
            event_id = sheet.cell(0, 0).value
            try:
                campus_event = CampusEvent.objects.get(pk=event_id)
            except Exception:
                raise BadRequest('编号为'+str(int(event_id))+'的活动不存在')
            # process the info of users
            for index in range(1, sheet.nrows):
                user_id = sheet.cell(index, 0).value

                try:
                    user = User.objects.get(pk=user_id)
                except Exception:
                    raise BadRequest('编号为'+str(int(user_id))+'的用户不存在')

                event_coefficient_id = sheet.cell(index, 1).value
                try:
                    event_coefficient = EventCoefficient.objects.get(
                        pk=event_coefficient_id)
                except Exception:
                    raise BadRequest('编号为'+str(int(event_coefficient_id)) +
                                     '的活动系数不存在')
                record = Record.objects.create(
                    campus_event=campus_event, user=user,
                    status=Record.STATUS_FEEDBACK_REQUIRED,
                    event_coefficient=event_coefficient)

                records.add(record)

        return len(records)


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
