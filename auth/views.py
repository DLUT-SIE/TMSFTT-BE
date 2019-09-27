'''Provide API views for auth module.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from rest_framework import viewsets, mixins, status, decorators
from rest_framework.response import Response
from rest_framework_bulk.mixins import BulkCreateModelMixin

from auth.services import DepartmentService
from auth.services import GroupService
import auth.models
import auth.serializers
import auth.permissions
import auth.filters
from infra.exceptions import BadRequest
from drf_cache.mixins import DRFCacheMixin

User = get_user_model()


class DepartmentViewSet(DRFCacheMixin, viewsets.ReadOnlyModelViewSet):
    '''Create API views for Department.'''
    queryset = auth.models.Department.objects.all()
    serializer_class = auth.serializers.DepartmentSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )

    @decorators.action(detail=False, methods=['GET'],
                       url_path='top-level-departments')
    def top_level_departments(self, request):
        '''return top level departments'''
        queryset = DepartmentService.get_top_level_departments()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(DRFCacheMixin, viewsets.ReadOnlyModelViewSet):
    '''Create API views for User.'''
    queryset = (
        User.objects
        .select_related('department', 'administrative_department')
        .prefetch_related('groups')
        .all()
        .order_by('id')
    )
    serializer_class = auth.serializers.UserSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )

    def _get_paginated_response(self, queryset):
        '''Return paginated response'''
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request):
        username = request.query_params.get('username', None)
        if username is None or username == '':
            raise BadRequest('请输入要查询的用户职工号')
        queryset = self.filter_queryset(self.get_queryset()).filter(
            username=username)
        return self._get_paginated_response(queryset)


class GroupViewSet(DRFCacheMixin, viewsets.ReadOnlyModelViewSet):
    '''Create API views for Group.'''
    queryset = Group.objects.all()
    serializer_class = auth.serializers.GroupSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )
    filter_class = auth.filters.GroupFilter

    @decorators.action(detail=False, methods=['GET'],
                       url_path='top-department-related-groups')
    def top_department_related_groups(self, request):
        '''return top department related groups'''
        department_id = request.GET.get('department_id')
        if department_id and not department_id.isdigit():
            raise BadRequest('部门ID无效')
        queryset = GroupService.get_all_groups_by_department_id(department_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserGroupViewSet(DRFCacheMixin,
                       mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    '''Create API views for GroupPermission.'''
    queryset = (
        auth.models.UserGroup.objects.all()
        .select_related('user')
    )
    serializer_class = auth.serializers.UserGroupSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )
    filter_fields = ('group',)


class GroupPermissionViewSet(DRFCacheMixin,
                             BulkCreateModelMixin,
                             viewsets.ModelViewSet):
    '''Create API views for GroupPermission.'''
    queryset = (
        auth.models.GroupPermission.objects.all()
    )
    serializer_class = auth.serializers.GroupPermissionSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )
    filter_fields = ('group',)


class PermissionViewSet(DRFCacheMixin, viewsets.ReadOnlyModelViewSet):
    '''Create READ-ONLY APIs for Permission.'''
    # Exclude Django-admin-related permissions.
    queryset = Permission.objects.filter(content_type_id__gt=13).all()
    serializer_class = auth.serializers.PermissionSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )
