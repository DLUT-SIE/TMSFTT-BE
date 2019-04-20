'''Define how to serialize our models.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from rest_framework import serializers

import auth.models


User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Department instance.'''
    users = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    admins = serializers.SerializerMethodField(read_only=True)
    roles = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = auth.models.Department
        fields = ('id', 'name', 'users', 'admins', 'roles')

    def get_admins(self, obj):  # pylint: disable=no-self-use
        '''Get department admin ids.'''
        role = auth.models.Role.objects.filter(
            department_id=obj.id,
            role_type=auth.models.Role.ROLE_DEPT_ADMIN,
        )
        if not role:
            return []
        return role[0].users.all().values_list('id', flat=True)


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


class UserSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize User instance.'''
    department_str = serializers.CharField(
        source='department.name', read_only=True)
    group_str = serializers.SerializerMethodField(read_only=True)

    def get_group_str(self, obj):  # pylint: disable=no-self-use
        '''Get all the groups of a regular User.'''
        group_set = Group.objects.filter(user=obj)
        return group_set.values_list('name', flat=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'last_login', 'first_name', 'last_name',
                  'email', 'is_active', 'date_joined', 'user_permissions',
                  'department', 'department_str', 'user_permissions',
                  'is_teacher', 'is_department_admin', 'is_school_admin',
                  'group_str')
