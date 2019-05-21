'''Provide services of training program module.'''
from django.db import transaction

from training_program.models import Program
from auth.services import PermissionService


class ProgramService:
    '''Provide services for Program.'''
    @staticmethod
    def create_program(program_data, context=None):
        '''Create a Program with ObjectPermission.

        Parametsers
        ----------
        program_data: dict
            This dict should have full information needed to
            create an Program.
        context: dict
            An optional dict to provide contextual information. Default: None

        Returns
        -------
        program: Program
        '''

        with transaction.atomic():
            program = Program.objects.create(**program_data)
            PermissionService.assign_object_permissions(
                context['request'].user, program)
            return program
