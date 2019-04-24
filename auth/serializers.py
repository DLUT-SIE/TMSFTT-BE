'''Define how to serialize our models.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import serializers

import auth.models


User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Department instance.'''
    users = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = auth.models.Department
        fields = ('id', 'name', 'users')

    # TODO: rewrite get_admins function


class PermissionSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Permission instance.'''
    label = serializers.CharField(source='name')

    class Meta:
        model = Permission
        fields = ('id', 'codename', 'label')


class UserPermissionSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize UserPermission instance.'''

    class Meta:
        model = auth.models.UserPermission
        fields = ('id', 'user', 'permission')


class GroupSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Group instance.'''

    class Meta:
        model = auth.models.Group
        fields = ('id', 'name')


class UserSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize User instance.'''
    department_str = serializers.CharField(
        source='department.name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'last_login', 'first_name', 'last_name',
                  'email', 'is_active', 'date_joined', 'user_permissions',
                  'department', 'department_str',
                  'is_teacher', 'is_department_admin', 'is_school_admin',
                  'groups')
