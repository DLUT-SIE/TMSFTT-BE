'''Unit tests for auth models.'''
from django.test import TestCase
from model_mommy import mommy

from auth.models import (
    User, Department, UserPermission, Role, GroupPermission,
    TeacherInformation, DepartmentInformation
)


class TestUser(TestCase):
    '''Unit tests for model User.'''
    def test_str(self):
        '''Should render string correctly.'''
        username = 'name'

        user = User(username=username)

        self.assertEqual(str(user), username)


class TestDepartment(TestCase):
    '''Unit tests for model Department.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'

        department = Department(name=name)

        self.assertEqual(str(department), name)


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


class TestRole(TestCase):
    '''Unit tests for model Role.'''
    def test_str(self):
        '''Should render string correctly.'''
        role_type, role_name = Role.ROLE_CHOICES[0]
        department = mommy.make(Department)
        name = '{}({})'.format(department, role_name)
        role = Role(department=department, role_type=role_type)

        self.assertEqual(str(role), name)


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
    def test_get_mapping_read_file(self):
        '''Should read from file if no cache found.'''
        self.assertIsNone(getattr(TeacherInformation, '_gender', None))

        # pylint: disable=protected-access
        TeacherInformation._get_mapping('gender')

        gender = getattr(TeacherInformation, '_gender', None)
        self.assertIsNotNone(gender)
        self.assertIsInstance(gender, dict)
        # pylint: disable=unsubscriptable-object
        self.assertEqual(gender['1'], '男性')
        self.assertEqual(gender['not-exist'], '未知')

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
