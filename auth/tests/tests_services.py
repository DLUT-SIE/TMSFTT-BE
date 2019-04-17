'''Unit tests for auth services.'''
from django.test import TestCase
from model_mommy import mommy

import auth.services as services
import auth.models as models
from infra.exceptions import BadRequest


class TestRoleService(TestCase):
    '''Unit tests for RoleService.'''
    def test_assign_roles_to_user_department_mismatch(self):
        '''Should raise BadRequest() if department mismatch.'''
        department1 = services.DepartmentService.create_department(
            {'name': 'department1'})
        department2 = services.DepartmentService.create_department(
            {'name': 'department2'})
        user = mommy.make(models.User, department=department1)

        with self.assertRaises(BadRequest):
            services.RoleService.assign_roles_to_user(
                user, department2.roles.all())

    def test_assign_roles_to_user(self):
        '''Should assign user to related groups.'''
        department = services.DepartmentService.create_department(
            {'name': 'department1'})
        user = mommy.make(models.User)

        services.RoleService.assign_roles_to_user(
            user, department.roles.all(),
            raise_error_for_department_mismatch=False)

        self.assertEqual(user.groups.count(), department.roles.count())

    def test_remove_roles_from_user(self):
        '''Should remove user from groups.'''
        cnt = 4
        roles = [mommy.make(models.Role) for _ in range(cnt)]
        user = mommy.make(models.User, roles=roles,
                          groups=[role.group for role in roles])

        self.assertEqual(user.groups.count(), cnt)
        self.assertEqual(user.roles.count(), cnt)

        services.RoleService.revoke_roles_from_user(user, roles)

        self.assertEqual(user.groups.count(), 0)
        self.assertEqual(user.roles.count(), 0)


class TestUserService(TestCase):
    '''Unit tests for UserService.'''
    def test_reassign_department(self):
        '''Should remove old roles and assign new roles.'''
        department1 = services.DepartmentService.create_department(
            {'name': 'department1'})
        department2 = services.DepartmentService.create_department(
            {'name': 'department2'})
        cnt = department1.roles.count()
        user = mommy.make(
            models.User,
            department=department1,
            roles=[role for role in department1.roles.all()],
            groups=[role.group for role in department1.roles.all()])

        self.assertEqual(user.groups.count(), cnt)
        self.assertEqual(user.roles.count(), cnt)

        services.UserService.reassign_department(user, department2)

        self.assertEqual(user.groups.count(), 0)
        self.assertEqual(user.roles.count(), 0)


class TestDepartmentService(TestCase):
    '''Unit tests for Department.'''
    def test_create_department(self):
        '''Should create department and its roles.'''
        department = services.DepartmentService.create_department(
            {'name': 'department'})

        roles = department.roles.all()
        self.assertEqual(roles.count(), len(models.Role.ROLE_CHOICES))
