'''Define workload calculation method.'''
from django.utils.timezone import now

from training_record.models import Record
from auth.models import User


class CoefficientCalculation:
    '''Provide workload calculation method .'''

    @staticmethod
    def calculate_workload_by_record(record):
        """
        calculate workload of record specified based on the eventCoefficient
        """
        if record.off_campus_event is None:
            return record.event_coefficient.calculate_campus_event_workload(
                record)
        return record.event_coefficient\
            .calculate_off_campus_event_workload(record)

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
                result[user_id] += record.event_coefficient\
                    .calculate_off_campus_event_workload(record)
                continue

            # 校内活动计算
            result[user_id] += record.event_coefficient\
                .calculate_campus_event_workload(record)
        return result
