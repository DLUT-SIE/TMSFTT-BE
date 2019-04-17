'''Provide services related to auth module.'''
# pylint: disable=too-few-public-methods
from django.contrib.auth import get_user_model
from django.db import transaction

from infra.exceptions import BadRequest

User = get_user_model()


class RoleService:
    '''Provide services related to roles.'''
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
                raise BadRequest()
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
    '''Provide services related to users.'''
    @staticmethod
    @transaction.atomic
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
        if user.department is not None:
            old_roles = user.department.roles.all()
            RoleService.remove_roles_from_user(user, old_roles)
        user.department = department
        user.save()
