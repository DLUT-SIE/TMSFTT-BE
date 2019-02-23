'''Provide services of traing event module.'''
from django.db import transaction
from django.contrib.auth.models import User

from training_event.models import OffCampusEvent
from training_record.models import Record, RecordContent, RecordAttachment


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
            raise ValueError('The off_campus_event_data is invalid')
        if user is None or not isinstance(user, User):
            raise ValueError('The user is invalid')
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
