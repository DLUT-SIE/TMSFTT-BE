'''Provide API views for training_program module.'''
from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
import training_program.models
import training_program.serializers


class ProgramViewSet(viewsets.ModelViewSet):
    '''Create API views for Progarm.'''
    queryset = training_program.models.Program.objects.all()
    serializer_class = training_program.serializers.ProgramSerializer


class ProgramCategoryViewSet(viewsets.ViewSet):
    '''get program categories from background.'''
    @decorators.action(detail=False, methods=['GET'],
                       url_path='')
    def get(self, request):
        '''return the program categories which are called '''
        program_category = [
            {
                'val': item[0],
                'name': item[1],
            } for item in training_program.models.Program.CATEGORY_CHOICES
        ]
        return Response(program_category, status=status.HTTP_200_OK)
