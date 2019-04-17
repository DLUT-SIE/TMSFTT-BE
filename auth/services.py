'''Provide services related to auth module.'''
# pylint: disable=too-few-public-methods
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

import auth.models
from infra.exceptions import BadRequest

User = get_user_model()


class RoleService:
    '''Provide services related to Role.'''
    @staticmethod
    def assign_roles_to_user(user, roles,
                             raise_error_for_department_mismatch=True):
        '''Assign new roles to user.

        Parameters
        ----------
        user: User object
            The target user.
        roles: Iterable of Role objects
            What role(s) should be assigned to the user.
        raise_error_for_department_mismatch: bool, default: True.
            Raise error if the user and the role have different department.
        '''
        if any(role.department_id != user.department_id for role in roles):
            if raise_error_for_department_mismatch:
                raise BadRequest('用户所在院系与用户组所在院系不一致')
            else:
                # TODO(youchen): Log the mismatch
                pass
        user.roles.add(*roles)
        groups = [role.group for role in roles]
        user.groups.add(*groups)

    @staticmethod
    def revoke_roles_from_user(user, roles):
        '''Remove the relation between the user and the roles.

        Parameters
        ----------
        user: User object
            The target user.
        roles: Iterable of Role objects
            What kind of role should be revoked from the target user.
        '''
        user.roles.remove(*roles)
        groups = [role.group for role in roles]
        user.groups.remove(*groups)


class UserService:
    '''Provide services related to User.'''
    @staticmethod
    def reassign_department(user, department):
        '''Reassign user to department.

        NOTE: If user is previously in another department, then his/her roles
        related to that department will be removed.

        Parameters
        ----------
        user: User object
            The target user of this action.
        department: Department object
            The new department the user should belong to.
        '''
        with transaction.atomic():
            if user.department is not None:
                old_roles = user.department.roles.all()
                RoleService.revoke_roles_from_user(user, old_roles)
            user.department = department
            user.save()


class DepartmentService:
    '''Provide services related to Department.'''
    @staticmethod
    def create_department(department_data):
        '''Create a new department based on given data.

        Related Group objects and Role objects will be created automatically.

        Parameters
        ----------
        department_data: dict
            Necessary data to create a department.

        Return
        ------
        deparment: Department object
            The created department.
        '''
        with transaction.atomic():
            department = auth.models.Department.objects.create(
                **department_data)
            roles = []
            for role_type, role_name in auth.models.Role.ROLE_CHOICES:
                group = Group.objects.create(name='{}({})'.format(
                    department.name, role_name))
                roles.append(auth.models.Role(
                    role_type=role_type, group=group, department=department))
            auth.models.Role.objects.bulk_create(roles)
            return department
