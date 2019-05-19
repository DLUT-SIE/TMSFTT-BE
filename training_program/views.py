'''Provide API views for training_program module.'''
import django_filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_guardian import filters

import auth.permissions
import training_program.models
import training_program.serializers
from infra.mixins import MultiSerializerActionClassMixin


class ProgramViewSet(MultiSerializerActionClassMixin, viewsets.ModelViewSet):
    '''Create API views for Progarm.'''
    queryset = training_program.models.Program.objects.all()
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
    filter_fields = ('department',)


class ProgramCategoryViewSet(viewsets.ViewSet):
    '''get program categories from background.'''
    def list(self, request):
        '''define how to get program categories'''
        program_categories = [
            {
                'type': item[0],
                'name': item[1],
            } for item in (
                training_program.models.Program.PROGRAM_CATEGORY_CHOICES)
        ]
        return Response(program_categories, status=status.HTTP_200_OK)
