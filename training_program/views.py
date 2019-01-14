'''Provide API views for training_program module.'''
from rest_framework import viewsets
import training_program.models
import training_program.serializers


class ProgramCategoryViewSet(viewsets.ModelViewSet):
    '''Create API views for ProgramCategory.'''
    queryset = training_program.models.ProgramCategory.objects.all()
    serializer_class = training_program.serializers.ProgramCategorySerializer


class ProgramFormViewSet(viewsets.ModelViewSet):
    '''Create API views for ProgarmForm.'''
    queryset = training_program.models.ProgramForm.objects.all()
    serializer_class = training_program.serializers.ProgramFormSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    '''Create API views for Progarm.'''
    queryset = training_program.models.Program.objects.all()
    serializer_class = training_program.serializers.ProgramSerializer
