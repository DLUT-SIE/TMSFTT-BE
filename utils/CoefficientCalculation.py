from training_event.models import EventCoefficient
from training_record.models import Record
from auth.models import Department, User

from django.utils.timezone import now
import math


class CoefficientCalculation:

    @staticmethod
    def calculate_campus_event_workload(record):
        event = record.campus_event
        event_coefficient = EventCoefficient.objects.select_related().all()\
            .filter(role=record.role, campus_event=event)[0]

        return CoefficientCalculation.calculate_workload(
            event.num_hours, event_coefficient.coefficient,
            event_coefficient.hours_option, event_coefficient.workload_option)

    @staticmethod
    def calculate_off_campus_event_workload(record):
        """
        return 0, if the record is a off_campus_event.
        """
        return 0

    @staticmethod
    def calculate_workload_by_record(record):
        """
        calculate workload of the record specified based on the eventCoefficient
        """
        if record.off_campus_event is None:
            return CoefficientCalculation\
                .calculate_campus_event_workload(record)
        return CoefficientCalculation.\
            calculate_off_campus_event_workload(record)

    @staticmethod
    def calculate_workload_by_query(department=None, start_time=None,
                                    end_time=None,):
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
            start_time = end_time.replace(year=end_time.year-1,
                                          month=12, day=31, hour=16, minute=0,
                                          second=0)
        if department is None:
            teachers = User.objects.all()
        else:
            teachers = User.objects.all().filter(department=department)
        # 查询缓存

        records = Record.objects.select_related(
            'event_coefficient', 'campus_event', 'off_campus_event').filter(
            user__in=teachers, campus_event__time__gte=start_time,
            campus_event__time__lte=end_time)

        result = {}
        for record in records:
            user_id = record.user_id
            result.setdefault(user_id, 0)
            # 校外活动计算
            if record.campus_event is None:
                result[user_id] += CoefficientCalculation\
                    .calculate_off_campus_event_workload(record)
                continue

            # 校内活动计算
            event_coefficient = record.event_coefficient
            result[user_id] += CoefficientCalculation.calculate_workload(
                record.campus_event.num_hours,
                event_coefficient.coefficient,
                event_coefficient.hours_option,
                event_coefficient.workload_option)
        return result

    @staticmethod
    def calculate_workload(num_hours, coefficient, hours_option=0,
                           workload_option=0):
        # calculate num_hours based on  hours_option
        hour = num_hours
        if hours_option == 1:
            hour = math.ceil(num_hours)
        elif hours_option == 2:
            hour = math.floor(num_hours)
        elif hours_option == 3:
            hour = round(num_hours)

        # calculate workload based on workload_option
        default_workload = hour * coefficient
        if workload_option == 0:
            return default_workload
        elif workload_option == 1:
            return math.ceil(default_workload)
        elif workload_option == 2:
            return math.floor(default_workload)
        return round(default_workload)



