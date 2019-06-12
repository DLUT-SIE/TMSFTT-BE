'''Utility functions provided by auth module.'''
import hashlib
import os.path as osp

import guardian.shortcuts
from django.conf import settings
from django.contrib.auth.models import Group

from infra.utils import prod_logger


def get_user_secret_key(user):
    '''Generate a secret key for a user.'''
    unhashed_key = '{}.{}'.format(
        settings.SECRET_KEY,  # Django secret key
        user.username,  # Username
        ).encode()
    sha1 = hashlib.new('sha1')
    sha1.update(unhashed_key)
    secret_key = sha1.hexdigest()
    return secret_key


def jwt_response_payload_handler(token, user=None, request=None):
    """Returns the response data for both the login and refresh views."""
    from auth.serializers import UserSerializer
    return {
        'user': UserSerializer(user).data,
        'token': token
    }


def assign_perm(perm_name, user_or_group, obj=None):
    '''Re-export assign_perm from django-guardian.'''
    ret = guardian.shortcuts.assign_perm(perm_name, user_or_group, obj)
    msg = (
        f'赋予用户(组) {user_or_group}'
        f' 对 {obj} 的 {perm_name} 权限'
    )
    prod_logger.info(msg)
    return ret


def remove_perm(perm_name, user_or_group, obj=None):
    '''Re-export remove_perm from django-guardian.'''
    return guardian.shortcuts.remove_perm(perm_name, user_or_group, obj)


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
        return cls._get_mapping_key_to_value().get(key, '未知')


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


def get_model_perms():
    '''Get perms map for models.'''
    from infra.models import Notification
    from training_program.models import Program
    from training_event.models import CampusEvent, Enrollment
    from training_record.models import (
        Record, RecordContent, RecordAttachment, CampusEventFeedback
    )
    from training_review.models import ReviewNote
    from secure_file.models import SecureFile

    return {
        Notification: {
            '管理员': [],
            '专任教师': [],
        },
        # Program
        Program: {
            '管理员': ['add', 'view', 'change', 'delete'],
            '专任教师': ['view'],
        },
        # Event
        CampusEvent: {
            '管理员': ['add', 'view', 'change', 'delete'],
            '专任教师': ['view'],
        },
        Enrollment: {
            '管理员': [],
            '专任教师': [],
        },
        # Record
        Record: {
            '管理员': ['batchadd', 'view', 'review', 'change'],
            '专任教师': [],
        },
        RecordContent: {
            '管理员': ['view'],
            '专任教师': [],
        },
        RecordAttachment: {
            '管理员': ['view'],
            '专任教师': [],
        },
        CampusEventFeedback: {
            '管理员': [],
            '专任教师': [],
        },
        # Review
        ReviewNote: {
            '管理员': ['add', 'view'],
            '专任教师': [],
        },
        SecureFile: {
            '管理员': ['view'],
            '专任教师': [],
        },
    }


# pylint: disable=too-many-locals
def assign_model_perms_for_department(department):
    '''Assign default model permissions for department groups.'''
    model_perms = get_model_perms()

    for model_class, perm_pairs in model_perms.items():
        for role, perms in perm_pairs.items():
            group = Group.objects.get(name=(
                f'{department.name}-{department.raw_department_id}-{role}'))
            for perm in perms:
                perm_name = (
                    f'{model_class._meta.app_label}.'
                    f'{perm}_{model_class._meta.model_name}'
                )
                assign_perm(perm_name, group)
