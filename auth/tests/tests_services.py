'''Unit tests for auth services.'''
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from model_mommy import mommy

import auth.services as services
from auth.models import Department
from training_event.models import CampusEvent

User = get_user_model()

PERMINSSION_MAP = ('add_campusevent',
                   'view_campusevent',
                   'change_campusevent',
                   'delete_campusevent')


class TestPermissonsService(TestCase):
    '''Unit tests for ObjectPermissonsManager.'''
    @classmethod
    def setUpTestData(cls):
        cls.permissionService = services.PermissonsService()
        cls.object = mommy.make(CampusEvent)
        cls.object_fake = mommy.make(Department)
        cls.perms = Permission.objects.filter(codename__in=PERMINSSION_MAP)

    def test_assigin_group_permissions_user(self):
        '''Should True if user has permissions of the related project.'''
        user = mommy.make(User)
        group = mommy.make(Group, name="大连理工大学-专任教师")
        group.permissions.add(*(perm for perm in self.perms))

        # pylint: disable=W0212
        self.permissionService._assigin_group_permissions(
            group, user, self.object)

        for perms in PERMINSSION_MAP:
            self.assertTrue(user.has_perm(perms, self.object))
        self.assertFalse(user.has_perm('add_record', self.object))
        self.assertFalse(user.has_perm('add_campusevent', self.object_fake))

    def test_assigin_group_permissions_group(self):
        '''Should True if user has permissions of the related project.'''
        user = mommy.make(User)
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)
        group.permissions.add(*(perm for perm in self.perms))

        # pylint: disable=W0212
        self.permissionService._assigin_group_permissions(
            group, group, self.object)

        for perms in PERMINSSION_MAP:
            self.assertTrue(user.has_perm(perms, self.object))
        self.assertFalse(user.has_perm('add_record', self.object))
        self.assertFalse(user.has_perm('add_campusevent', self.object_fake))

    def test_assigin_object_permissions(self):
        '''Should True if user has permissions of the related project.'''
        department_school = mommy.make(Department, name="大连理工大学")
        department_admin = mommy.make(
            Department, name="创新创业学院", super_department=department_school)

        user = mommy.make(User, department=department_admin)
        group = mommy.make(Group, name="大连理工大学-专任教师")

        group_school = mommy.make(Group, name="大连理工大学-管理员")
        user_school = mommy.make(User)
        user_school.groups.add(group_school)

        group_admin = mommy.make(Group, name="创新创业学院-管理员")
        user_admin = mommy.make(User)
        user_admin.groups.add(group_admin)

        group.permissions.add(*(perm for perm in self.perms))
        group_admin.permissions.add(*(perm for perm in self.perms))
        group_school.permissions.add(*(perm for perm in self.perms))

        self.permissionService.assigin_object_permissions(user, self.object)

        for perms in PERMINSSION_MAP:
            self.assertTrue(user.has_perm(perms, self.object))
        self.assertFalse(user.has_perm('add_record', self.object))
        self.assertFalse(user.has_perm('add_campusevent', self.object_fake))

        for perms in PERMINSSION_MAP:
            self.assertTrue(user_admin.has_perm(perms, self.object))
        self.assertFalse(user_admin.has_perm('add_record', self.object))
        self.assertFalse(user_admin.has_perm(
            'add_campusevent', self.object_fake))

        for perms in PERMINSSION_MAP:
            self.assertTrue(user_school.has_perm(perms, self.object))
        self.assertFalse(user_school.has_perm('add_record', self.object))
        self.assertFalse(
            user_school.has_perm('add_campusevent', self.object_fake))


class TestDepartmentService(TestCase):
    '''Unit tests for DepartmentService.'''
    def test_get_top_level_departments(self):
        '''Should return top level departments'''
        depart1 = mommy.make(Department, name='大连理工大学')
        depart2 = mommy.make(
            Department, name='盘锦校区', super_department=depart1)
        depart3 = mommy.make(Department, name='电子信息与电气工程学部')
        depart4 = mommy.make(
            Department, super_department=depart2, department_type='T3')
        depart5 = mommy.make(
            Department, super_department=depart3, department_type='T3')

        queryset = services.DepartmentService.get_top_level_departments()

        self.assertTrue(queryset.filter(id=depart4.id).exists())
        self.assertFalse(queryset.filter(id=depart5.id).exists())


class TestGroupService(TestCase):
    '''Unit tests for GroupService.'''
    def test_get_top_level_departments(self):
        '''Should return top level departments'''
        depart1 = mommy.make(Department, name='大连理工大学')
        depart2 = mommy.make(
            Department, name='凌水主校区', super_department=depart1)
        mommy.make(
            Department, name='电子信息与电气工程学部', super_department=depart2)

        group1 = mommy.make(Group, name="大连理工大学-管理员")
        group2 = mommy.make(Group, name="凌水主校区-专任教师")
        group3 = mommy.make(Group, name="电子信息与电气工程学部-管理员")
        group4 = mommy.make(Group, name="创新创业学院-管理员")

        queryset = services.GroupService.get_all_groups_by_department_id(
            depart1.id)

        self.assertTrue(queryset.filter(id=group1.id).exists())
        self.assertTrue(queryset.filter(id=group2.id).exists())
        self.assertTrue(queryset.filter(id=group3.id).exists())
        self.assertFalse(queryset.filter(id=group4.id).exists())
