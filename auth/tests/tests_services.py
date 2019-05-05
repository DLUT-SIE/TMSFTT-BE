'''Unit tests for auth services.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from model_mommy import mommy
from django.test import TestCase
from training_event.models import CampusEvent

import auth.services as services
from auth.models import Department

User = get_user_model()

PERMINSSION_MAP = ('add_campusevent',
                   'view_campusevent',
                   'change_campusevent',
                   'delete_campusevent')


class TestObjectPermissonsService(TestCase):
    '''Unit tests for ObjectPermissonsManager.'''
    @classmethod
    def setUpTestData(cls):
        cls.permissionService = services.ObjectPermissonsService()
        cls.object = mommy.make(CampusEvent)
        cls.object_fake = mommy.make(Department)
        cls.perms = Permission.objects.filter(codename__in=PERMINSSION_MAP)

    def test_assigin_group_permissions_user(self):
        user = mommy.make(User)
        group = mommy.make(Group, name="大连理工大学-专任教师")
        for permission in PERMINSSION_MAP:
            group.permissions.add(*(perm for perm in self.perms))

        self.permissionService.assigin_group_permissions(
            group, user, self.object)

        for perms in PERMINSSION_MAP:
            self.assertTrue(user.has_perm(perms, self.object))
        self.assertFalse(user.has_perm('add_record', self.object))
        self.assertFalse(user.has_perm('add_campusevent', self.object_fake))

    def test_assigin_group_permissions_group(self):
        user = mommy.make(User)
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)
        for permission in PERMINSSION_MAP:
            group.permissions.add(*(perm for perm in self.perms))

        self.permissionService.assigin_group_permissions(
            group, group, self.object)

        for perms in PERMINSSION_MAP:
            self.assertTrue(user.has_perm(perms, self.object))
        self.assertFalse(user.has_perm('add_record', self.object))
        self.assertFalse(user.has_perm('add_campusevent', self.object_fake))

    def test_assigin_object_permissions(self):
        department = mommy.make(Department, name="创新创业学院")
        user = mommy.make(User, department=department)
        group = mommy.make(Group, name="大连理工大学-专任教师")

        group_ad = mommy.make(Group, name="创新创业学院-管理员")
        user_ad = mommy.make(User)
        user_ad.groups.add(group_ad)

        group_add = mommy.make(Group, name="大连理工大学-领导")
        user_add = mommy.make(User)
        user_add.groups.add(group_add)

        for permission in PERMINSSION_MAP:
            group.permissions.add(*(perm for perm in self.perms))

        for permission in PERMINSSION_MAP:
            group_ad.permissions.add(*(perm for perm in self.perms))

        for permission in PERMINSSION_MAP:
            group_add.permissions.add(*(perm for perm in self.perms))

        self.permissionService.assigin_object_permissions(user, self.object)

        for perms in PERMINSSION_MAP:
            self.assertTrue(user.has_perm(perms, self.object))
        self.assertFalse(user.has_perm('add_record', self.object))
        self.assertFalse(user.has_perm('add_campusevent', self.object_fake))

        for perms in PERMINSSION_MAP:
            self.assertTrue(user_ad.has_perm(perms, self.object))
        self.assertFalse(user_ad.has_perm('add_record', self.object))
        self.assertFalse(user_ad.has_perm('add_campusevent', self.object_fake))

        for perms in PERMINSSION_MAP:
            self.assertTrue(user_add.has_perm(perms, self.object))
        self.assertFalse(user_add.has_perm('add_record', self.object))
        self.assertFalse(
            user_add.has_perm('add_campusevent', self.object_fake))


class DummyConverter(services.ChoiceConverter):
    '''Read test mapping.'''
    mapping_name = 'test'


class TestChoiceConverter(TestCase):
    '''Unit tests for ChoiceConverter.'''
    def setUp(self):
        self.key_to_value_field_name = '_test_key_to_value'
        self.value_to_key_field_name = '_test_value_to_key'
        if hasattr(DummyConverter, self.key_to_value_field_name):
            del DummyConverter._test_key_to_value
        if hasattr(DummyConverter, self.value_to_key_field_name):
            del DummyConverter._test_value_to_key

    def test_get_mapping_read_file(self):
        '''Should read from file if no cache found.'''
        field_name = self.key_to_value_field_name
        self.assertIsNone(getattr(DummyConverter, field_name, None))

        # pylint: disable=protected-access
        DummyConverter._get_mapping_key_to_value()

        mapping = getattr(DummyConverter, field_name, None)
        self.assertIsNotNone(mapping)
        self.assertIsInstance(mapping, dict)
        # pylint: disable=unsubscriptable-object
        self.assertEqual(mapping['0'], 'A')
        self.assertEqual(mapping['1'], 'B')

    def test_get_key(self):
        '''Should return key.'''
        expected_key = '0'
        key = DummyConverter.get_key('A')

        self.assertEqual(key, expected_key)

    def test_get_value(self):
        '''Should return value.'''
        expected_value = 'C'
        value = DummyConverter.get_value('2')

        self.assertEqual(value, expected_value)

    def test_get_keys(self):
        '''Should return all keys.'''
        expected_keys = {'0', '1', '2'}
        keys = set(DummyConverter.get_all_keys())

        self.assertEqual(keys, expected_keys)
