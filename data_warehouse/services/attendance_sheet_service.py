'''Service for export attendance sheet'''
from training_event.models import (
    CampusEvent, Enrollment
)
from auth.models import User


class AttendanceSheetService:
    '''Service for attendance sheet'''
    @staticmethod
    def get_user(event_id):
        '''get matched user'''
        enrolled_users = list(Enrollment.objects.filter(
            campus_event=event_id
        ).values_list('user_id', flat=True))
        if enrolled_users:
            return User.objects.filter(
                id__in=enrolled_users
            )
        return None
    
    @staticmethod
    def get_event(event_id):
        '''get matched event'''
        matched_event = CampusEvent.objects.get(pk=event_id)
        return matched_event