'''Provide services related to auth module.'''
import os.path as osp
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from django.db import transaction
from auth.utils import assign_perm
import auth.models


class PermissonsService:
    '''Provide services for Permissons.'''
    # pylint: disable=redefined-builtin
    @classmethod
    @transaction.atomic()
    def assigin_object_permissions(cls, user=None, instance=None):
        '''
        The function is used to provide permissions for releated user when
        an object is created (a teacher create a tranning record for exmaple).
        Parameters
        ----------
        user: User
            the current user who create the object.
        instance: Model
            a model instance
        Returns
        -------
        None
        '''
        # i: assgin User-Object-Permissions for the current user
        group = Group.objects.get(name='大连理工大学-专任教师')
        cls._assigin_group_permissions(group, user, instance)

        # ii: assgin Group-Object-Permissions for DepartmentGroup
        related_department = user.department
        while related_department:
            for group in Group.objects.filter(
                    name__startswith=related_department.name).exclude(
                        name='大连理工大学-专任教师'):
                cls._assigin_group_permissions(group, group, instance)
            related_department = related_department.super_department

    # pylint: disable=redefined-builtin
    @classmethod
    def _assigin_group_permissions(
            cls, group=None, user_or_group=None, instance=None):
        '''
        The function is used to assign object-level-permissons to an user or a
        group based on model-permissions of a given group.

        Parameters
        ----------
        group: Group
            the group which provide model-permissions
        user_or_group: User or Group
            an user or a group which is going to get object-level-permissons
        instance: Model
            a model instance
        Returns
        -------
        None
        '''
        content_type = ContentType.objects.get_for_model(
            instance._meta.model)
        for perm in group.permissions.all().filter(
                content_type_id=content_type.id):
            assign_perm(perm, user_or_group, instance)


class DepartmentService:
    '''
    Provide services for Departments.
    '''
    @staticmethod
    def get_top_level_departments():
        '''Get top level departments.

        Returns
        -------
        result: dict
            the dict of top_level_departments
        '''
        departments = auth.models.Department.objects.filter(name='大连理工大学')
        department_id = []
        if departments.exists():
            department = departments[0]
            department_id = [
                item.id for item in auth.models.Department.objects.all(
                    ).filter(super_department=department)]
        return auth.models.Department.objects.all().filter(
                super_department__in=department_id, department_type='T3')


class ChoiceConverter:
    '''
    A helper converter to convert values between keys and values.
    '''
    mapping_name = None

    @classmethod
    def _get_mapping_key_to_value(cls):
        '''Read mapping from ./data/<mapping_name>.

        Parameters
        ----------
        mapping_name: string
            The mapping file name.

        Return
        ------
        mapping_dict: dict
            The code to human-readable string mapping dict.
        '''
        assert cls.mapping_name
        private_mapping_name = f'_{cls.mapping_name}_key_to_value'
        if not hasattr(cls, private_mapping_name):
            mapping = {}
            fpath = osp.join(osp.dirname(__file__), 'data', cls.mapping_name)
            with open(fpath) as target_file:
                for line in target_file:
                    mapping.setdefault(*line.strip().split())
            # pylint: disable=attribute-defined-outside-init
            setattr(cls, private_mapping_name, mapping)
        return getattr(cls, private_mapping_name)

    @classmethod
    def _get_mapping_value_to_key(cls):
        private_mapping_name = f'_{cls.mapping_name}_value_to_key'
        if not hasattr(cls, private_mapping_name):
            mapping = cls._get_mapping_key_to_value()
            mapping = {value: key for key, value in mapping.items()}
            setattr(cls, private_mapping_name, mapping)
        return getattr(cls, private_mapping_name)

    @classmethod
    def get_key(cls, value):
        '''Return key w.r.t value.

        Parameters
        ----------
        value: str
            The corresponding value to the return key.

        Return
        ------
        key: str
            The key to the value.
        '''
        return cls._get_mapping_value_to_key()[value]

    @classmethod
    def get_all_keys(cls):
        '''Return all keys.

        Return
        ------
        keys: dict_keys
            All keys read.
        '''
        return cls._get_mapping_key_to_value().keys()

    @classmethod
    def get_value(cls, key):
        '''Return value w.r.t key.

        Parameters
        ----------
        key: str
            The corresponding key to the return value.

        Return
        ------
        value: str
            The value to the key.
        '''
        return cls._get_mapping_key_to_value()[key]


class EducationBackgroundConverter(ChoiceConverter):
    '''Convert between education background pairs.'''
    mapping_name = 'education_background'


class TechnicalTitleConverter(ChoiceConverter):
    '''Convert between technical title pairs.'''
    mapping_name = 'technical_title'


class GenderConverter(ChoiceConverter):
    '''Convert between gender pairs.'''
    mapping_name = 'gender'


class TenureStatusConverter(ChoiceConverter):
    '''Convert between tenure status pairs.'''
    mapping_name = 'tenure_status'


class TeachingTypeConverter(ChoiceConverter):
    '''Convert between teaching type pairs.'''
    mapping_name = 'teaching_type'
