'''Provide services related to auth module.'''
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from django.db import transaction

from auth.utils import assign_perm
from auth.models import Department, UserGroup
from infra.services import NotificationService
from infra.utils import prod_logger


class PermissonsService:
    '''Provide services for Permissons.'''
    # pylint: disable=redefined-builtin
    @classmethod
    @transaction.atomic()
    def assigin_object_permissions(cls, user=None, instance=None):
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
        group = Group.objects.get(name='大连理工大学-专任教师')
        cls._assigin_group_permissions(group, user, instance)

        # ii: assgin Group-Object-Permissions for DepartmentGroup
        related_department = user.department
        while related_department:
            for group in Group.objects.filter(
                    name__startswith=related_department.name).exclude(
                        name='大连理工大学-专任教师'):
                cls._assigin_group_permissions(group, group, instance)
            related_department = related_department.super_department

    # pylint: disable=redefined-builtin
    @classmethod
    def _assigin_group_permissions(
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
                '为用户/组%s赋予Object-Level权限%s', user_or_group, perm)


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
        prod_logger.info('取得所有大连理工大学的顶级学部学院')
        departments = Department.objects.filter(name='大连理工大学')
        top_department = []
        if departments.exists():
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
        prod_logger.info('取得%s(学部学院)的所有用户组', departments[0])
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

        with transaction.atomic():
            usergroup = UserGroup.objects.create(
                user=user, group=group)
            content = '用户{}被加入用户组{}中'.format(user, group)
            prod_logger.info(content)
            NotificationService.send_system_notification(user, content)
            return usergroup
