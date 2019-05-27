'''Provide services related to auth module.'''
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from django.db import transaction

from auth.utils import assign_perm
from auth.models import Department, UserGroup, User
from infra.utils import prod_logger


class PermissionService:
    '''Provide services for Permissons.'''
    # pylint: disable=redefined-builtin
    @classmethod
    @transaction.atomic()
    def assign_object_permissions(cls, user=None, instance=None):
        '''
        The function is used to provide permissions for releated user when
        an object is created (a teacher create a tranning record for exmaple).
        Parameters
        ----------
        user: User
            the current user who create the object.
        instance: Model
            a model instance
        Returns
        -------
        None
        '''

        # i: assgin User-Object-Permissions for the current user
        group = Group.objects.get(name='个人权限')
        cls._assign_group_permissions(group, user, instance)

        # ii: assgin Group-Object-Permissions for DepartmentGroup
        related_department = user.department
        while related_department:
            for group in Group.objects.filter(
                    name__startswith=f'{related_department.name}-'):
                cls._assign_group_permissions(group, group, instance)
            related_department = related_department.super_department

    # pylint: disable=redefined-builtin
    @classmethod
    def _assign_group_permissions(
            cls, group=None, user_or_group=None, instance=None):
        '''
        The function is used to assign object-level-permissons to an user or a
        group based on model-permissions of a given group.

        Parameters
        ----------
        group: Group
            the group which provide model-permissions
        user_or_group: User or Group
            an user or a group which is going to get object-level-permissons
        instance: Model
            a model instance
        Returns
        -------
        None
        '''
        content_type = ContentType.objects.get_for_model(
            instance._meta.model)
        for perm in group.permissions.all().filter(
                content_type_id=content_type.id):
            assign_perm(perm, user_or_group, instance)
            prod_logger.info(
                '赋予用户/用户组 %s 对 %s 对象的 %s 权限',
                user_or_group, instance, perm)


class UserService:
    '''Provide services for User.'''
    @staticmethod
    def get_full_time_teachers():
        '''Return queryset for full time teachers.'''
        return User.objects.filter(
            teaching_type__in=('专任教师', '实验技术')
        )


class DepartmentService:
    '''
    Provide services for Departments.
    '''
    @staticmethod
    def get_top_level_departments():
        '''Get top level departments.

        Returns
        -------
        result: dict
            the dict of top_level_departments
        '''
        departments = Department.objects.filter(name='大连理工大学')
        top_department = []
        if departments:
            dlut_department = departments[0]
            top_department = dlut_department.child_departments.all()
        return Department.objects.all().filter(
            super_department__in=top_department, department_type='T3')


class GroupService:
    '''
    Provide services for Groups.
    '''
    # pylint: disable=redefined-builtin
    @staticmethod
    def get_all_groups_by_department_id(department_id):
        '''Get all Groups by DepartmentId.
        Parameters
        ------------
        id: int
            the id of target Top Department
        Returns
        -------
        result: queryset
            the queryset of all the groups which belongs to a
            top_level_department
        '''
        departments = list(Department.objects.filter(id=department_id))
        if not departments:
            return []
        search_list = departments
        while search_list:
            search_list = list(Department.objects.filter(
                super_department__in=[d.id for d in search_list]))
            departments.extend(search_list)
        regex = '^({})'.format('|'.join(d.name for d in departments))
        return Group.objects.filter(name__regex=regex)


class UserGroupService:
    '''
    Provide services for UserGroups.
    '''
    @staticmethod
    def add_user_to_group(user=None, group=None):
        '''Add a user to a group with notification.

        Parametsers
        ----------
        user: User
            related user
        group: Group
            related group
        Returns
        -------
        usergroup: UserGroup
        '''
        from infra.services import NotificationService

        with transaction.atomic():
            usergroup = UserGroup.objects.create(
                user=user, group=group)
            content = (f'用户({user.first_name}-{user.username})'
                       f'被加入用户组({group})中')
            prod_logger.info(content)
            NotificationService.send_system_notification(user, content)
            return usergroup
