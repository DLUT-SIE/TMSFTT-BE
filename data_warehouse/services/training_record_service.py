'''Service for export records'''
from django.utils.timezone import datetime
from django.db.models import Q
from training_record.models import Record


class TrainingRecordService:
    '''Service for export records'''
    @staticmethod
    def get_records(user, event_name=None,
                    event_location=None, start_time=None, end_time=None):
        '''get matched records'''
        if event_name is None:
            event_name = ''
        if event_location is None:
            event_location = ''
        if start_time == '' or start_time is None:
            start_time = datetime.strptime(
                '1900-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        if end_time == '' or end_time is None:
            end_time = datetime.now()
        return Record.objects.filter(
            Q(user=user),
            (
                Q(off_campus_event__name__startswith=event_name) &
                Q(off_campus_event__location__startswith=event_location) &
                Q(off_campus_event__time__gte=start_time) &
                Q(off_campus_event__time__lte=end_time)
            ) | (
                Q(campus_event__name__startswith=event_name) &
                Q(campus_event__location__startswith=event_location) &
                Q(campus_event__time__gte=start_time) &
                Q(campus_event__time__lte=end_time)
            )
        )
