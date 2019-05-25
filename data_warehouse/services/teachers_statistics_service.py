'''provide teachers statistics relevant methods'''
from django.db.models import Count

from data_warehouse.consts import EnumData
from auth.models import (Department, User)
from auth.services import DepartmentService
from infra.exceptions import BadRequest


class TeachersStatisticsService:
    '''get teachers statistics data'''

    @classmethod
    def teachers_statistics_group_dispatch(cls, users, group_by, count_only):
        ''' dispatch group_by function by group_by

        Parameters:
        ----------
        users: QuerySet
        group_by: int
        count_only: boolean
        '''
        group_by_handler = {
            EnumData.BY_TECHNICAL_TITLE: cls.group_users_by_technical_title,
            EnumData.BY_HIGHEST_DEGREE: (
                cls.group_users_by_education_background),
            EnumData.BY_AGE_DISTRIBUTION: cls.group_users_by_age,
            EnumData.BY_DEPARTMENT: cls.group_users_by_department
        }
        if group_by not in group_by_handler:
            raise BadRequest("错误的参数")
        return group_by_handler[group_by](users, count_only=count_only)

    @staticmethod
    def group_users_by_technical_title(users, count_only=False):
        '''
        Return
        ------
        group_users: dict
        {
            '教授': [USER_A, USER_B],
        } for count_only=False
        or
        {
            '教授': 3,
        } for count_only=True
        '''
        title_list = EnumData.TITLE_LABEL
        if count_only:
            total_count = users.count()
            group_users = {x: 0 for x in title_list}
            users = users.filter(
                technical_title__in=title_list).values(
                    'technical_title').annotate(count=Count('technical_title'))
            sum_count = 0
            for user in users:
                sum_count += user['count']
                group_users[user['technical_title']] = user['count']
            group_users['其他'] = total_count - sum_count
        else:
            group_users = {
                x: User.objects.none() for x in title_list}
            for _, title in enumerate(title_list):
                group_users[title] = users.filter(technical_title=title)
            group_users['其他'] = users.exclude(technical_title__in=title_list)
        return group_users

    @staticmethod
    def group_users_by_education_background(users, count_only=False):
        '''
        Return
        ------
        group_users: dict
        {
            '本科毕业': [USER_A, USER_B],
        } for count_only=False
        or
        {
            '本科毕业': 3,
        } for count_only=True
        '''
        education_background_list = EnumData.EDUCATION_BACKGROUD_LABEL
        if count_only:
            group_users = {x: 0 for x in education_background_list}
            users = users.filter(
                education_background__in=education_background_list).values(
                    'education_background').annotate(
                        count=Count('education_background'))
            for user in users:
                group_users[user['education_background']] = user['count']
        else:
            group_users = {
                x: (
                    User.objects.none()
                ) for x in education_background_list}
            for _, degree in enumerate(education_background_list):
                group_users[degree] = users.filter(
                    education_background=degree)
        return group_users

    @staticmethod
    def group_users_by_department(users, count_only=False):
        '''
        Return
        ------
        group_users: dict
        {
            '创新学院': [USER_A, USER_B],
        } for count_only=False
        or
        {
            '创新学院': 3,
        } for count_only=True
        '''
        department_list = list(
            DepartmentService.get_top_level_departments().values_list('name'))
        department_list = [x[0] for x in department_list]
        if count_only:
            group_users = {x: 0 for x in department_list}
            users = (
                users.filter(
                    administrative_department__name__in=department_list)
                .values('administrative_department__name')
                .annotate(count=Count('id'))
            )
            for user in users:
                group_users[user['administrative_department__name']] = (
                    user['count']
                )
        else:
            group_users = {
                x: User.objects.none() for x in department_list}
            for _, degree in enumerate(department_list):
                group_users[degree] = users.filter(
                    administrative_department__name=degree)
        return group_users

    @staticmethod
    def group_users_by_age(users, count_only=False):
        '''
        Return
        ------
        group_users: dict
        {
            '35岁及以下': [USER_A, USER_B],
        } for count_only=False
        or
        {
            '35岁及以下': 3,
        } for count_only=Truerecords
        '''
        age_list = ((0, 35), (36, 45), (46, 55), (56, 1000))
        label_list = EnumData.AGE_LABEL
        group_users = {}
        if count_only:
            for index, value in enumerate(age_list):
                group_users[label_list[index]] = users.filter(
                    age__range=value).count()
        else:
            for index, value in enumerate(age_list):
                group_users[label_list[index]] = users.filter(age__range=value)
        return group_users

    @staticmethod
    def get_users_by_department(request_user, department_id):
        '''get users objects by department.
        Parameters:
        ----------
        request_user: User
        department_id: int

        Return: QuerySet<User>
        '''
        queryset = User.objects.all().select_related(
            'administrative_department')
        departments = Department.objects.filter(id=department_id)
        if not departments:
            return User.objects.none()
        department = departments[0]
        if request_user.is_school_admin:
            if department.name == '大连理工大学':
                return queryset
            return queryset.filter(
                administrative_department__id=department.id)
        if request_user.check_department_admin(department):
            return queryset.filter(
                administrative_department__id=department.id)
        return User.objects.none()
