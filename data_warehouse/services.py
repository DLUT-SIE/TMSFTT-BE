'''Provide services of data graph.'''
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user

from infra.exceptions import BadRequest


class AggregateDataService:
    '''provide services for getting data'''

    STAFF_STATISTICS = 0
    TRAINEE_STATISTICS = 1
    FULL_TIME_TEACHER_TRAINED_COVERAGE = 2
    TRAINING_HOURS_WORKLOAD_STATISTICS = 3

    BY_DEPARTMENT = 0
    BY_TEACHING_TYPE = 1
    BY_STAFF_TITLE = 2
    BY_HIGHEST_DEGREE = 3
    BY_AGE_DISTRIBUTION = 4

    BY_DEPARTMENT = 0
    BY_STAFF_TITLE = 1
    BY_AGE_DISTRIBUTION = 2

    BY_TOTAL_STAFF_NUM = 0
    BY_TOTAL_TRAINING_HOURS = 1
    BY_PER_CAPITA_TRAINING_HOURS = 2
    BY_TOTAL_WORKLOAD = 3
    BY_PER_CAPITA_WORKLOAD = 4

    STAFF_GROUPING_CHOICES = (
        (BY_DEPARTMENT, '按学院', 'BY_DEPARTMENT'),
        (BY_TEACHING_TYPE, '按人员类别', 'BY_TEACHING_TYPE'),
        (BY_STAFF_TITLE, '按职称', 'BY_STAFF_TITLE'),
        (BY_HIGHEST_DEGREE, '按最高学位', 'BY_HIGHEST_DEGREE'),
        (BY_AGE_DISTRIBUTION, '按年龄分布', 'BY_AGE_DISTRIBUTION')
    )
    TRAINEE_GROUPING_CHOICES = (
        (BY_DEPARTMENT, '按学院', 'BY_DEPARTMENT'),
        (BY_STAFF_TITLE, '按职称', 'BY_STAFF_TITLE'),
        (BY_AGE_DISTRIBUTION, '按年龄分布', 'BY_AGE_DISTRIBUTION')
    )
    TRAINING_HOURS_GROUPING_CHOICES = (
        (BY_TOTAL_STAFF_NUM, '按总人数', 'BY_TOTAL_STAFF_NUM'),
        (BY_TOTAL_TRAINING_HOURS, '按总培训学时', 'BY_TOTAL_TRAINING_HOURS'),
        (BY_PER_CAPITA_TRAINING_HOURS, '按人均培训学时', 'BY_PER_CAPITA_\
            TRAINING_HOURS'),
        (BY_TOTAL_WORKLOAD, '按总工作量', 'BY_TOTAL_WORKLOAD'),
        (BY_PER_CAPITA_WORKLOAD, '按人均工作量', 'BY_PER_CAPITA_WORKLOAD')
    )

    @classmethod
    def dispatch(cls, request, graph_type, graph_options):
        '''to call a specific service for getting data'''
        statistics_method_map = {
            cls.STAFF_STATISTICS: cls.staff_statistics,
            cls.TRAINEE_STATISTICS: cls.trainee_statistics,
            cls.FULL_TIME_TEACHER_TRAINED_COVERAGE: cls.coverage_statistics,
            cls.TRAINING_HOURS_WORKLOAD_STATISTICS:
                cls.training_hours_statistics
        }
        graph_type = int(graph_type)
        if graph_type not in statistics_method_map.keys():
            raise BadRequest("错误的参数格式")
        return statistics_method_map[graph_type](request.user, graph_options)

    @classmethod
    def staff_statistics(cls, request_user, graph_options):
        '''to get staff statistics data'''

    @classmethod
    def trainee_statistics(cls, request_user, graph_options):
        '''to get trainee statistics data'''

    @classmethod
    def coverage_statistics(cls, request_user, graph_options):
        '''to get coverage statistics data'''

    @classmethod
    def training_hours_statistics(cls, request_user, graph_options):
        '''to get training hours statistics data'''

    @staticmethod
    def group_by_teaching_type(objects, start_year, end_year, region):
        '''group data by teaching type'''

    @staticmethod
    def tuple_to_dict_list(data):
        '''return a data dict list'''
        return [{
            'type': type_num,
            'name': name,
            'key': key_name
            } for type_num, name, key_name in data]

    @classmethod
    def get_canvas_options(cls):
        '''return a data graph select dictionary'''
        statistics_type = [
            {'type': cls.STAFF_STATISTICS,
             'name': '教职工人数统计',
             'key': 'STAFF_STATISTICS',
             'subOption': cls.tuple_to_dict_list(cls.STAFF_GROUPING_CHOICES)},
            {'type': cls.TRAINEE_STATISTICS,
             'name': '培训人数统计',
             'key': 'TRAINEE_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 cls.TRAINEE_GROUPING_CHOICES)},
            {'type': cls.FULL_TIME_TEACHER_TRAINED_COVERAGE,
             'name': '专任教师培训覆盖率统计',
             'key': 'FULL_TIME_TEACHER_TRAINED_COVERAGE',
             'subOption': cls.tuple_to_dict_list(
                 cls.TRAINEE_GROUPING_CHOICES)},
            {'type': cls.TRAINING_HOURS_WORKLOAD_STATISTICS,
             'name': '培训学时与工作量统计',
             'key': 'TRAINING_HOURS_WORKLOAD_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 cls.TRAINING_HOURS_GROUPING_CHOICES)}
        ]
        return statistics_type
