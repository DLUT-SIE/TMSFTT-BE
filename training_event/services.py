'''Provide services of training event module.'''
from django.db import transaction
from django.utils.timezone import now

from infra.exceptions import BadRequest
from training_event.models import CampusEvent, Enrollment
from training_record.models import Record

from auth.models import User


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


class CoefficientCalculationService:
    '''Provide workload calculation method .'''

    @staticmethod
    def calculate_workload_by_query(department=None, start_time=None,
                                    end_time=None, ):
        """calculate workload by department and period

        Parameters
        ----------
        start_time: date
            查询起始时间
        end_time: date
            查询结束时间
        department: Department
            查询的学院
        Returns
        -------
        result: dict
        key 为学部老师
        values 为该老师在规定查询时间段内的工时
        """
        if end_time is None:
            end_time = now()
        if start_time is None:
            start_time = end_time.replace(year=end_time.year - 1,
                                          month=12, day=31, hour=16, minute=0,
                                          second=0)
        if department is None:
            teachers = User.objects.all()
        else:
            teachers = User.objects.all().filter(department=department)
        # 查询缓存

        campus_records = Record.objects.select_related(
            'event_coefficient', 'campus_event').filter(
                user__in=teachers,
                campus_event__time__gte=start_time,
                campus_event__time__lte=end_time)

        off_campus_records = Record.objects.select_related(
            'event_coefficient', 'off_campus_event').filter(
                user__in=teachers, off_campus_event__time__gte=start_time,
                off_campus_event__time__lte=end_time)
        result = {}

        for record in campus_records:
            user_id = record.user_id
            result.setdefault(user_id, 0)

            # 校内活动计算
            result[user_id] += record.event_coefficient \
                .calculate_campus_event_workload(record)

        for record in off_campus_records:
            user_id = record.user_id
            result.setdefault(user_id, 0)
            # 校外活动计算
            if record.campus_event is None:
                result[user_id] += record.event_coefficient \
                    .calculate_off_campus_event_workload(record)
                continue
        return result
