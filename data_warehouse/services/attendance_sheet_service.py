'''Service for export attendance sheet'''
from training_event.models import Enrollment


class AttendanceSheetService:
    '''Service for attendance sheet'''
    @staticmethod
    def get_enrollment(event_id):
        '''get matched enrollment'''
        return Enrollment.objects.filter(
            campus_event_id=event_id).select_related(
                'user__department', 'campus_event'
            )
