'''provide canvas data formater service'''
from data_warehouse.consts import EnumData
from auth.services import DepartmentService


class CanvasDataFormater:
    '''format data for canvas'''

    @staticmethod
    def format_records_statistics_data(group_records):
        ''' format records statistics data

        Parameters:
        ----------
        group_records: dict
            {
                'campus_records': dict
                'off_campus_records': dict
            }
        '''
        data = {
            'label': [],
            'group_by_data': [
                {
                    'seriesNum': 0,
                    'seriesName': '校内培训',
                    'data': []
                },
                {
                    'seriesNum': 1,
                    'seriesName': '校外培训',
                    'data': []
                }
            ]
        }
        random_key = list(group_records['campus_records'].keys())[0]
        labels = [
            EnumData.AGE_LABEL,
            EnumData.EDUCATION_BACKGROUD_LABEL,
            EnumData.TITLE_LABEL
        ]
        for label in labels:
            if random_key in label:
                data['label'] = label
                break
        if not data['label']:
            data['label'] = list(group_records['campus_records'].keys())
        for label in data['label']:
            data['group_by_data'][0]['data'].append(
                group_records['campus_records'][label] if (
                    label in group_records['campus_records']) else 0)
            data['group_by_data'][1]['data'].append(
                group_records['off_campus_records'][label] if (
                    label in group_records['off_campus_records']) else 0)
        return data

    @staticmethod
    def format_teachers_statistics_data(group_users):
        '''format statistics data

        Parameters:
        ----------
        group_users: dict
        '''
        data = {
            'label': [],
            'group_by_data': [
                {
                    'seriesNum': 0,
                    'seriesName': '专任教师',
                    'data': []
                }
            ]
        }
        if not group_users:
            return data
        random_key = list(group_users.keys())[0]
        labels = [
            EnumData.AGE_LABEL,
            EnumData.EDUCATION_BACKGROUD_LABEL,
            EnumData.TITLE_LABEL
        ]
        for label in labels:
            if random_key in label:
                data['label'] = label
                break
        if not data['label']:
            data['label'] = list(group_users.keys())
        for label in data['label']:
            data['group_by_data'][0]['data'].append(
                group_users[label] if (
                    label in group_users) else 0)
        return data

    @staticmethod
    def format_coverage_statistics_data(group_users):
        '''format coverage statistics data

        Parameters:
        ----------
        group_users: list of dict
            [
                {
                    "age_range" or "title" or "department": "35岁及以下",
                    "coverage_count": 0,
                    "total_count": 965
                }
            ]
        '''
        data = {
            'label': [],
            'group_by_data': [
                {
                    'seriesNum': 0,
                    'seriesName': '覆盖人数',
                    'data': []
                },
                {
                    'seriesNum': 1,
                    'seriesName': '未覆盖人数',
                    'data': []
                }
            ]
        }
        if not bool(group_users):
            return data
        interest_label = None
        if 'age_range' in group_users[0].keys():
            label_key = 'age_range'
            interest_label = EnumData.AGE_LABEL
        elif 'department' in group_users[0].keys():
            label_key = 'department'
            interest_label = list(
                DepartmentService
                .get_top_level_departments()
                .values_list('name', flat=True))
        else:
            label_key = 'title'
            interest_label = EnumData.TITLE_LABEL
        for user in group_users:
            if interest_label and user[label_key] not in interest_label:
                continue
            data['label'].append(user[label_key])
            data['group_by_data'][0]['data'].append(user['coverage_count'])
            data['group_by_data'][1]['data'].append(
                user['total_count'] - user['coverage_count'])
        return data
