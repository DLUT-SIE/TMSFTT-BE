'''Provide services of training program module.'''
from django.db import transaction

from training_program.models import Program
from auth.services import PermissionService
from infra.utils import prod_logger


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
            user = context['request'].user
            msg = (f'用户{user}创建了培训机构为'
                   + f'{program.department}的培训项目{program.name}')
            prod_logger.info(msg)
            PermissionService.assigin_object_permissions(
                context['request'].user, program)
            return program

    @staticmethod
    def update_program(program, validated_data, context=None):
        '''Update program

        Parameters
        ----------
        program: Program
            The program we will update.
        category: Categoty
            The categoty of which the program is related to.
        name: The program's name

        Returns
        -------
        program: Program
        '''

        # update the program
        for attr, value in validated_data.items():
            setattr(program, attr, value)
        program.save()

        # log the update
        user = context['request'].user
        msg = (f'用户{user}修改了培训机构为'
               + f'{program.department}的培训项目{program.name}')
        prod_logger.info(msg)
        return program
