'''Unit tests for auth models.'''
from django.test import TestCase
from django.contrib.auth.models import Group
from model_mommy import mommy

from auth.models import (
    User, Department, UserPermission, GroupPermission,
    TeacherInformation, DepartmentInformation
)

import auth.models


class TestUser(TestCase):
    '''Unit tests for model User.'''
    def test_str(self):
        '''Should render string correctly.'''
        username = 'name'

        user = User(username=username)

        self.assertEqual(str(user), username)

    def test_is_teacher(self):
        '''Should return True if user is a teacher.'''
        user = mommy.make(auth.models.User)
        group = mommy.make(Group, name="创新创业学院-专任教师")
        user.groups.add(group)

        self.assertTrue(user.is_teacher)
        self.assertFalse(user.is_department_admin)
        self.assertFalse(user.is_school_admin)

    def test_is_department_admin(self):
        '''Should return True if user is a department admin.'''
        user = mommy.make(auth.models.User)
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)

        self.assertFalse(user.is_teacher)
        self.assertTrue(user.is_department_admin)
        self.assertFalse(user.is_school_admin)

    def test_is_school_admin(self):
        '''Should return True if user is a school admin.'''
        user = mommy.make(auth.models.User)
        group = mommy.make(Group, name="大连理工大学-管理员")
        user.groups.add(group)

        self.assertFalse(user.is_teacher)
        self.assertTrue(user.is_department_admin)
        self.assertTrue(user.is_school_admin)

    def test_check_department_admin(self):
        '''Should return True if user is a exact department admin.'''
        department1 = mommy.make(Department, name="创新创业学院")
        department2 = mommy.make(Department, name="机械工程学院")
        user = mommy.make(auth.models.User)
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)

        self.assertTrue(user.check_department_admin(department1))
        self.assertFalse(user.check_department_admin(department2))


class TestDepartment(TestCase):
    '''Unit tests for model Department.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'

        department = Department(name=name)

        self.assertEqual(str(department), name)


class TestUserGroup(TestCase):
    '''Unit tests for model UserGroup.'''
    def test_str(self):
        '''Should reder string correctly'''
        user_id = 1
        group_id = 2
        expected_str = '用户{}位于用户组{}中'.format(user_id, group_id)

        user_group = auth.models.UserGroup(
            user_id=user_id,
            group_id=group_id)

        self.assertEqual(str(user_group), expected_str)


class TestUserPermission(TestCase):
    '''Unit tests for model UserPermission.'''
    def test_str(self):
        '''Should render string correctly.'''
        user_id = 1
        permission_id = 2
        expected_str = '用户{}拥有权限{}'.format(user_id, permission_id)

        user_permission = UserPermission(
            user_id=user_id,
            permission_id=permission_id)

        self.assertEqual(str(user_permission), expected_str)


class TestGroupPermission(TestCase):
    '''Unit tests for model GroupPermission.'''
    def test_str(self):
        '''Should render string correctly.'''
        group_id = 1
        permission_id = 2
        expected_str = '用户组{}拥有权限{}'.format(group_id, permission_id)

        group_permission = GroupPermission(
            group_id=group_id,
            permission_id=permission_id)

        self.assertEqual(str(group_permission), expected_str)


class TestTeacherInformation(TestCase):
    '''Unit tests for TeacherInformation.'''
    def test_get_xl_display(self):
        '''Should return human-readable string.'''
        info = TeacherInformation(xl='11')

        self.assertEqual(info.get_xl_display(), '博士研究生毕业')

    def test_get_zyjszc_display(self):
        '''Should return human-readable string.'''
        info = TeacherInformation(zyjszc='061')

        self.assertEqual(info.get_zyjszc_display(), '研究员')

    def test_get_xb_display(self):
        '''Should return human-readable string.'''
        info = TeacherInformation(xb='2')

        self.assertEqual(info.get_xb_display(), '女性')

    def test_get_rzzt_display(self):
        '''Should return human-readable string.'''
        info = TeacherInformation(rzzt='11')

        self.assertEqual(info.get_rzzt_display(), '在职')

    def test_get_rjlx_display(self):
        '''Should return human-readable string.'''
        info = TeacherInformation(rjlx='21')

        self.assertEqual(info.get_rjlx_display(), '院系机关')

    def test_save_should_be_disallowed(self):
        '''Should raise error if trying to save model.'''
        info = TeacherInformation()

        with self.assertRaisesMessage(Exception, '该表状态为只读'):
            info.save()

    def test_delete_should_be_disallowed(self):
        '''Should raise error if trying to save model.'''
        info = TeacherInformation()

        with self.assertRaisesMessage(Exception, '该表状态为只读'):
            info.delete()


class TestDepartmentInformation(TestCase):
    '''Unit tests for DepartmentInformation.'''
    def test_save_should_be_disallowed(self):
        '''Should raise error if trying to save model.'''
        info = DepartmentInformation()

        with self.assertRaisesMessage(Exception, '该表状态为只读'):
            info.save()

    def test_delete_should_be_disallowed(self):
        '''Should raise error if trying to save model.'''
        info = DepartmentInformation()

        with self.assertRaisesMessage(Exception, '该表状态为只读'):
            info.delete()
