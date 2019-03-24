'''Provide services of training event module.'''
from django.db import transaction

from infra.exceptions import BadRequest
from training_event.models import CampusEvent, Enrollment


# pylint: disable=too-few-public-methods
class EnrollmentService:
    '''Provide services for Enrollment.'''
    @staticmethod
    def create_enrollment(enrollment_data):
        '''Create a enrollment for specific campus event.

        This action is atomic, will fail if there are no more head counts for
        the campus event or duplicated enrollments are created.

        Parameters
        ----------
        enrollment_data: dict
            This dict should have full information needed to
            create an Enrollment.

        Returns
        -------
        enrollment: Enrollment
        '''
        with transaction.atomic():
            # Lock the event until the end of the transaction
            event = CampusEvent.objects.select_for_update().get(
                id=enrollment_data['campus_event'].id)

            if event.num_enrolled >= event.num_participants:
                raise BadRequest('报名人数已满')

            enrollment = Enrollment.objects.create(**enrollment_data)

            # Update the number of enrolled participants
            event.num_enrolled += 1
            event.save()

            return enrollment
