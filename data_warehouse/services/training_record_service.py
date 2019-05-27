'''Service for export records'''
from django.db.models import Q
from training_record.models import Record


class TrainingRecordService:
    '''Service for export records'''
    @staticmethod
    def get_records(user, event_name,
                    event_location, start_time, end_time):
        '''get matched records'''
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
