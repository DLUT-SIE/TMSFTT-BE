'''Provide services related to auth module.'''
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group
from auth.utils import assign_perm
from django.db import transaction


class ObjectPermissonsService():
    '''Provide services for ObjectPermissons.'''
    @staticmethod
    def assigin_object_permissions(user, object):
        """
        The function is used to provide permissions for releated user when
        an object is created (a teacher create a tranning record for exmaple).
        Parameters
        ----------
        user: User
            the current user who create the object.
        object: Model
            an model instance
        Returns
        -------
        None
        """
        with transaction.atomic():
            # i: assgin User-Object-Permissions for the current user
            group = Group.objects.get(name='大连理工大学-专任教师')
            ObjectPermissonsService().assigin_group_permissions(
                group, user, object)

            # ii: assgin Group-Object-Permissions for DepartmentAdmin
            for group in Group.objects.filter(
                    name__startswith=user.department.name):
                ObjectPermissonsService().assigin_group_permissions(
                    group, group, object)

            # ii: assgin Group-Object-Permissions for SchoolGroup
            for group in Group.objects.filter(
                name__startswith='大连理工大学').exclude(
                    name='大连理工大学-专任教师'):
                        ObjectPermissonsService().assigin_group_permissions(
                            group, group, object)

    @staticmethod
    def assigin_group_permissions(group, user_or_group, object):
        """
        The function is used to assign object-level-permissons to an user or a
        group based on model-permissions of a given group.

        Parameters
        ----------
        group: Group
            the group which provide model-permissions
        user_or_group: User or Group
            an user or a group which is going to get object-level-permissons
        object: Model
            an model instance
        Returns
        -------
        None
        """
        contenttype = ContentType.objects.get_for_model(object._meta.model)
        group_perms_id = [
            perms.id for perms in group.permissions.all()]
        for perm in Permission.objects.filter(
                content_type_id=contenttype.id, id__in=group_perms_id):
            assign_perm(perm.codename, user_or_group, object)
