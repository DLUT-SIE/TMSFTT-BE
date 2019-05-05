'''Unit tests for auth serializers.'''
from django.contrib.auth.models import Group
from django.test import TestCase
from model_mommy import mommy

import auth.models as models
import auth.serializers as serializers


class TestDepartmentSerializer(TestCase):
    '''Unit tests for DepartmentSerializer.'''

    def test_get_non_admins(self):
        '''Should return empty list if no such admins.'''
        department = mommy.make(models.Department)
        admin = serializers.DepartmentSerializer().get_admins(department)

        self.assertEqual(admin, [])

    def test_get_admins(self):
        '''Should return list of ids if admins exist.'''
        cnt = 10

        department = mommy.make(models.Department)
        group = mommy.make(Group, name=department.name+"-管理员")
        users = [mommy.make(models.User) for _ in range(cnt)]
        for user in users:
            user.groups.add(group)

        admin = set(serializers.DepartmentSerializer().get_admins(department))
        self.assertEqual(admin, set(user.id for user in users))
