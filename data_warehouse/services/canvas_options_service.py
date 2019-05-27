'''provide canvas options service'''
from data_warehouse.consts import EnumData


class CanvasOptionsService:
    '''provide canvas options service'''

    @staticmethod
    def tuple_to_dict_list(data):
        '''return a data dict list'''
        return [{'type': type_num, 'name': name, 'key': key_name} for
                type_num, name, key_name in data]

    @classmethod
    def get_canvas_options(cls):
        '''return a data graph select dictionary'''
        statistics_type = [
            {'type': EnumData.TEACHERS_STATISTICS,
             'name': '教职工人数统计',
             'key': 'TEACHERS_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 EnumData.TEACHERS_GROUPING_CHOICES)},
            {'type': EnumData.RECORDS_STATISTICS,
             'name': '培训人数统计',
             'key': 'RECORDS_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 EnumData.TRAINEE_GROUPING_CHOICES)},
            {'type': EnumData.COVERAGE_STATISTICS,
             'name': '专任教师培训覆盖率统计',
             'key': 'COVERAGE_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 EnumData.TRAINEE_GROUPING_CHOICES)},
            {'type': EnumData.TRAINING_HOURS_STATISTICS,
             'name': '培训学时与工作量统计',
             'key': 'TRAINING_HOURS_STATISTICS',
             'subOption': []}
        ]
        return statistics_type
