'''REST permission checkers.'''
from django.http import Http404
from rest_framework import permissions, exceptions

from infra.utils import prod_logger


SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
STANDARD_ACTIONS = ('create', 'retrieve', 'list', 'update',
                    'partial', 'destroy')


class SchoolAdminOnlyPermission(permissions.BasePermission):
    '''Only school admin has access to resources.'''
    message = '需要拥有学校管理员身份才能访问。'

    def has_permission(self, request, view):
        '''Check school admin role.'''
        return request.user.is_authenticated and request.user.is_school_admin


class DjangoModelPermissions(permissions.DjangoModelPermissions):
    '''Require model permissions for resources.

    This is similar to the one provided by DRF, but add support for custom
    permissions for extra actions. You can also override perms for default
    action names, such as list, retrieve, update, etc.

    If `perms_map` has been defined on the view, and current action is not a
    standard action (such as list, partial_update, destroy, etc), then the
    permissions must be configured for the custom action, otherwise an error
    with 403 will be raised.

    You can provide permission names in view's `perms_map` as a format string,
    `%(app_label)s` and `%(model_name)s` will be replaced based on the queryset
    of the view, for example, `%(app_label)s.view_%(model_name)s` on
    viewset for `Notification` will be formatted into `infra.view_notification`.

    Example
    -------
    class MyViewSet(viewsets.ModelViewSet):
        permission_classes = (DjangoModelPermissions,)
        perms_map = {
            'custom_action': ['%(app_label)s.permission_name'],
        }

        @decorators.action(...)
        def custom_action(self):
            pass
    '''
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def get_required_permissions(self, method, view, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        perms_map = self.perms_map
        if method not in perms_map:
            raise exceptions.MethodNotAllowed(method)

        view_perms_map = getattr(view, 'perms_map', {})
        is_standard_action = view.action in STANDARD_ACTIONS
        if (is_standard_action is False
                and (view_perms_map is None
                     or view.action not in view_perms_map)):
            # Action is a custom action But perms_map of view is None or
            # permissions are not configured for the action in the perms_map
            log = (
                f'{view}视图中{view.action}为非标准操作，'
                f'但并未找到相应权限设置(perms_map)，请及时修复'
            )
            prod_logger.warning(log)
            raise exceptions.PermissionDenied(
                '未找到相应权限设置，请联系系统管理员')
        elif is_standard_action is False or view.action in view_perms_map:
            # Permissions for the action are configured in view's perms_map
            perms_map = view_perms_map
            method = view.action

        return [perm % kwargs for perm in perms_map[method]]

    def has_permission(self, request, view):
        '''This method is similar to default `DjangoModelPermission`. But we've
        add support for check custom permissions for extra actions.'''
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or (
                not request.user.is_authenticated
                and self.authenticated_users_only):
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(
            request.method, view, queryset.model)

        return request.user.has_perms(perms)


class DjangoObjectPermissions(DjangoModelPermissions):
    '''Require object permissions for resources.

    This class is inherited from `DjangoModelPermissions`, and has same
    permission checking logic with its parent class, so there is no need to
    add `DjangoModelPermissions` in `permission_classes` section if this class
    presented.'''
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def get_required_object_permissions(self, method, view, model_cls):
        '''Get object permissions names.

        The logic for getting object permissions is the same as
        `get_required_permission`, so we just reuse it.
        '''
        return self.get_required_permissions(method, view, model_cls)

    def has_object_permission(self, request, view, obj):
        '''Check object permission.'''
        # authentication checks have already executed via has_permission
        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(
            request.method, view, model_cls)

        if not user.has_perms(perms, obj):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions(
                'GET', view, model_cls)
            if not user.has_perms(read_perms, obj):
                raise Http404

            # Has read permissions.
            return False

        return True
