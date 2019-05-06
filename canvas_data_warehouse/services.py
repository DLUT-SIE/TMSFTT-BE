'''Provide services of data graph.'''


class CanvasDataService:
    '''provide services for getting canvas data'''

    STAFF_STATISTICS = 0
    TRAINEE_STATISTICS = 1
    FULL_TIME_TEACHER_TRAINED_COVERAGE = 2
    TRAINING_HOURS_WORKLOAD_STATISTICS = 3

    BY_DEPARTMENT = 0
    BY_STAFF_TYPE = 1
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

    staff_grouping_type = (
        (BY_DEPARTMENT, '按学院'),
        (BY_STAFF_TYPE, '按人员类别'),
        (BY_STAFF_TITLE, '按职称'),
        (BY_HIGHEST_DEGREE, '按最高学位'),
        (BY_AGE_DISTRIBUTION, '按年龄分布')
    )
    trainee_grouping_type = (
        (BY_DEPARTMENT, '按学院'),
        (BY_STAFF_TITLE, '按职称'),
        (BY_AGE_DISTRIBUTION, '按年龄分布')
    )
    training_hours_grouping_type = (
        (BY_TOTAL_STAFF_NUM, '按总人数'),
        (BY_TOTAL_TRAINING_HOURS, '按总培训学时'),
        (BY_PER_CAPITA_TRAINING_HOURS, '按人均培训学时'),
        (BY_TOTAL_WORKLOAD, '按总工作量'),
        (BY_PER_CAPITA_WORKLOAD, '按人均工作量')
    )

    @classmethod
    def dispatch(cls, graph_type, graph_options):
        '''to call a specific service for getting data'''

    @staticmethod
    def tuple_to_dict_list(data):
        '''return a data dict list'''
        return [{'type': key, 'name': val} for key, val in data]

    @classmethod
    def get_graph_param(cls):
        '''return a data graph select dictionary'''
        statistics_type = [
            {'type': cls.STAFF_STATISTICS,
             'option': {'name': '教职工人数统计', 'subOption': cls.tuple_to_dict_list(
                 cls.staff_grouping_type)}},
            {'type': cls.TRAINEE_STATISTICS,
             'option': {'name': '培训人数统计', 'subOption': cls.tuple_to_dict_list(
                 cls.trainee_grouping_type)}},
            {'type': cls.FULL_TIME_TEACHER_TRAINED_COVERAGE,
             'option': {'name': '专任教师培训覆盖率统计', 'subOption':
                        cls.tuple_to_dict_list(cls.trainee_grouping_type)}},
            {'type': cls.TRAINING_HOURS_WORKLOAD_STATISTICS,
             'option': {'name': '培训学时与工作量统计', 'subOption':
                        cls.tuple_to_dict_list(
                            cls.training_hours_grouping_type)}}
        ]
        return statistics_type
