'''Provide services of training record module.'''
import tempfile
import xlrd

from django.db import transaction
from django.contrib.auth import get_user_model

from infra.exceptions import BadRequest
from training_event.models import OffCampusEvent, CampusEvent
from training_record.models import Record


User = get_user_model()


# pylint: disable=too-few-public-methods
class RecordService:
    '''Provide services for Record.'''
    @staticmethod
    def create_off_campus_record_from_raw_data(
            off_campus_event=None, user=None,
            contents=None, attachments=None):
        '''Create a off-campus-record from raw data.'''

        if off_campus_event is None or not isinstance(off_campus_event,
                                                      OffCampusEvent):
            raise BadRequest('校外培训活动无效')
        if user is None or not isinstance(user, User):
            raise BadRequest('用户无效')
        if contents is None:
            contents = []
        if attachments is None:
            attachments = []

        with transaction.atomic():

            record = Record.objects.create(
                off_campus_event=off_campus_event,
                user=user,
            )

            for content in contents:
                content.record = record
                content.save()

            for attachment in attachments:
                attachment.record = record
                attachment.save()

        return record

    @staticmethod
    def create_campus_records_from_excel(file):
        '''Create a training record of off-campus training event.

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

        # process for each event
        for index in range(sheet.ncols):

            # get the information
            ids = sheet.col_values(index)
            event_id = ids[0]
            user_ids = ids[1:]
            try:
                campus_event = CampusEvent.objects.get(pk=event_id)
            except Exception:
                raise BadRequest('编号为'+str(int(event_id))+'的活动不存在')

            # generate the record for each participant
            for user_id in user_ids:

                try:
                    user = User.objects.get(pk=user_id)
                except Exception:
                    raise BadRequest('编号为'+str(int(user_id))+'的用户不存在')

                record = Record.objects.create(
                    campus_event=campus_event, user=user)

                records.add(record)

        return len(records)
