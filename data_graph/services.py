'''Provide services of data graph.'''
from auth.models import Department


class StatisticsType():
    '''provide graph params StatisticsType enum'''
    STAFF_STATISTICS = 0
    TRAINEE_STATISTICS = 1
    FULL_TIME_TEACHER_TRAINED_COVERAGE = 2
    TRAINING_HOURS_WORKLOAD_STATISTICS = 3


class StaffGroupingType():
    '''provide graph params StaffGroupingType enum'''
    BY_DEPARTMENT = 0
    BY_STAFF_TYPE = 1
    BY_STAFF_TITLE = 2
    BY_HIGHEST_DEGREE = 3
    BY_AGE_DISTRIBUTION = 4


class TraineeNumberCoverageGroupingType():
    '''provide graph params TraineeNumberCoverageGroupingType enum'''
    BY_DEPARTMENT = 0
    BY_STAFF_TITLE = 1
    BY_AGE_DISTRIBUTION = 2


class TrainHoursWorkloadGroupingType():
    '''provide graph params TrainHoursWorkloadGroupingType enum'''
    BY_TOTAL_STAFF_NUM = 0
    BY_TOTAL_TRAINING_HOURS = 1
    BY_PER_CAPITA_TRAINING_HOURS = 2
    BY_TOTAL_WORKLOAD = 3
    BY_PER_CAPITA_WORKLOAD = 4


class DataGraphService:
    '''Provide services for selecting data-get services'''

    @staticmethod
    def select_sub_service(request_data):
        pass


class DataGraphParamsService:
    '''provide services for getting all graph params'''
    staff_grouping_type = [
        {'type': StaffGroupingType.BY_DEPARTMENT, 'name': '按学院'},
        {'type': StaffGroupingType.BY_STAFF_TYPE, 'name': '按人员类别'},
        {'type': StaffGroupingType.BY_STAFF_TITLE, 'name': '按职称'},
        {'type': StaffGroupingType.BY_HIGHEST_DEGREE, 'name': '按最高学位'},
        {'type': StaffGroupingType.BY_AGE_DISTRIBUTION, 'name': '按年龄分布'}
    ]
    trainee_number_coverage_grouping_type = [
        {
            'type': TraineeNumberCoverageGroupingType.BY_DEPARTMENT,
            'name': '按学院'
        },
        {
            'type': TraineeNumberCoverageGroupingType.BY_STAFF_TITLE,
            'name': '按职称'
        },
        {
            'type': TraineeNumberCoverageGroupingType.BY_AGE_DISTRIBUTION,
            'name': '按年龄分布'
        }
    ]
    training_hours_workload_grouping_type = [
        {'type': TrainHoursWorkloadGroupingType.BY_TOTAL_STAFF_NUM,
         'name': '按总人数'},
        {'type': TrainHoursWorkloadGroupingType.BY_TOTAL_TRAINING_HOURS,
         'name': '按总培训学时'},
        {'type': TrainHoursWorkloadGroupingType.BY_PER_CAPITA_TRAINING_HOURS,
         'name': '按人均培训学时'},
        {'type': TrainHoursWorkloadGroupingType.BY_TOTAL_WORKLOAD,
         'name': '按总工作量'},
        {'type': TrainHoursWorkloadGroupingType.BY_PER_CAPITA_WORKLOAD,
         'name': '按人均工作量'}
    ]
    statistics_type = [
        {'type': StatisticsType.STAFF_STATISTICS,
         'option': {'name': '教职工人数统计', 'subOption': staff_grouping_type}},
        {'type': StatisticsType.TRAINEE_STATISTICS,
         'option': {'name': '培训人数统计',
                    'subOption': trainee_number_coverage_grouping_type}},
        {'type': StatisticsType.FULL_TIME_TEACHER_TRAINED_COVERAGE,
         'option': {'name': '专任教师培训覆盖率统计',
                    'subOption': trainee_number_coverage_grouping_type}},
        {'type': StatisticsType.TRAINING_HOURS_WORKLOAD_STATISTICS,
         'option': {'name': '培训学时与工作量统计',
                    'subOption': training_hours_workload_grouping_type}}
    ]

    @classmethod
    def get_graph_param(cls):
        departments = Department.objects.all()
        departments = [department.name for department in departments]
        data = {
            'statistics_type': cls.statistics_type,
            'departments': departments
        }
        return data
