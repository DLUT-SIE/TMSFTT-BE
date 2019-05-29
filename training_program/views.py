'''Provide API views for training_program module.'''
import django_filters
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
from rest_framework import views, viewsets, status
from rest_framework.response import Response
from rest_framework_guardian import filters

import auth.permissions
import training_program.filters
import training_program.models
import training_program.serializers
from training_program.services import ProgramService
from infra.mixins import MultiSerializerActionClassMixin


class ProgramViewSet(MultiSerializerActionClassMixin, viewsets.ModelViewSet):
    '''Create API views for Progarm.'''
    queryset = (
        training_program.models.Program.objects.all()
        .select_related('department')
    )
    serializer_class = training_program.serializers.ProgramSerializer
    serializer_action_classes = {
        'create': training_program.serializers.ProgramSerializer,
        'partial_update': training_program.serializers.ProgramSerializer,
        'update': training_program.serializers.ProgramSerializer,
    }
    serializer_class = training_program.serializers.ReadOnlyProgramSerializer
    filter_backends = (filters.DjangoObjectPermissionsFilter,
                       django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (
        auth.permissions.DjangoObjectPermissions,
    )
    filter_class = training_program.filters.ProgramFilter
    perms_map = {
        'get_group_programs': ['%(app_label)s.view_%(model_name)s']
    }

    @method_decorator(cache_page(60))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @action(detail=False, url_path='group-programs', url_name='group')
    def get_group_programs(self, request):
        '''get group programs'''
        group_programs = ProgramService.get_grouped_programs_by_department(
            request.user)
        return Response(group_programs, status=status.HTTP_200_OK)


class ProgramCategoryView(views.APIView):
    '''get program categories from background.'''
    def get(self, request, format=None):  # pylint: disable=redefined-builtin
        '''define how to get program categories'''
        cache_key = 'program-categories'
        program_categories = cache.get(cache_key)
        if program_categories is None:
            program_categories = [
                {
                    'type': program_type,
                    'name': program_type_name,
                } for program_type, program_type_name in (
                    training_program.models.Program.PROGRAM_CATEGORY_CHOICES)
            ]
            cache.set(cache_key, program_categories, 10 * 60)
        return Response(program_categories, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
