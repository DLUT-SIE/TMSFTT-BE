'''Provide API views for training_program module.'''
from rest_framework import viewsets, status
from rest_framework.response import Response
import training_program.models
import training_program.serializers


class ProgramViewSet(viewsets.ModelViewSet):
    '''Create API views for Progarm.'''
    queryset = training_program.models.Program.objects.all()
    serializer_class = training_program.serializers.ProgramSerializer


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
