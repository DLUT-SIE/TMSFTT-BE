import xlrd
import tempfile
import os

'''Provide services of training record module.'''
from django.db import transaction
from django.contrib.auth import get_user_model

from infra.exceptions import BadRequest
from training_event.models import OffCampusEvent, CampusEvent
from training_record.models import Record, RecordContent, RecordAttachment


User = get_user_model()


# pylint: disable=too-few-public-methods
class RecordService:
    '''Provide services for Record.'''
    @staticmethod
    def create_off_campus_record_from_raw_data(
            off_campus_event_data=None, user=None,
            contents_data=None, attachments_data=None):
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

            record = Record.objects.create(
                off_campus_event=off_campus_event,
                user=user,
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
    def create_campus_records_from_excel(request):
        '''Create a training record of off-campus training event.

        Parameters
        ----------
        file: excel
            This file should have full information needed to create a
            Record of campus-event.
            The first line should be the id of each campus-event.
            For each campus-event, the id of its participant should be below its id.

        Returns
        -------
        count of records
        '''

        records = set()

        #get excel from request
        file = request.FILES['file'].read()
        tup = tempfile.mkstemp()
        with open(tup[0],'wb') as f:
            f.write(file)

        #open excel
        workbook = xlrd.open_workbook(tup[1])

        # get the first sheet
        sheet = workbook.sheet_by_index(0)

        #get the number of events
        num_event = sheet.ncols

        #process for each event
        for index in range(num_event):

            #get the information
            ids = sheet.col_values(index)
            event_id = ids[0]
            user_ids =ids[1:]
            try:
                campus_event = CampusEvent.objects.get(pk=event_id)
            except Exception:
                raise BadRequest('编号为'+str(event_id)+'的活动不存在')
            
            #generate the record for each participant
            for user_id in user_ids:

                try:
                    user = User.objects.get(pk=user_id)
                except Exception:
                    raise BadRequest('编号为'+str(user_id)+'的用户不存在')

                record = Record.objects.create(
                    campus_event=campus_event, user=user)

                records.add(record)

        return len(records)



            
            
