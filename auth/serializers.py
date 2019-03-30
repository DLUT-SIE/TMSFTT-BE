'''Define how to serialize our models.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import serializers

import auth.models


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize User instance.'''
    user_permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'last_login', 'first_name', 'last_name',
                  'email', 'is_active', 'date_joined', 'user_permissions')

    def get_user_permissions(self, obj):  # pylint: disable=no-self-use
        '''Populate user's permissions list.'''
        permissions = auth.models.UserPermission.objects.filter(user=obj)
        return UserPermissionSerializer(permissions, many=True).data


class DepartmentSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Department instance.'''
    admins_detail = UserSerializer(source='admins', read_only=True,
                                   many=True)

    class Meta:
        model = auth.models.Department
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize UserProfile instance.'''
    class Meta:
        model = auth.models.UserProfile
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Permission instance.'''
    label = serializers.CharField(source='name')

    class Meta:
        model = Permission
        fields = ('id', 'codename', 'label')


class UserPermissionSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize UserPermission instance.'''
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        style={'base_template': 'input.html'},
    )
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        style={'base_template': 'input.html'},
        write_only=True,
        source='permission',
    )

    class Meta:
        model = auth.models.UserPermission
        fields = ('id', 'user', 'permission', 'permission_id')
