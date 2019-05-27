'''Provide services of training program module.'''
from collections import defaultdict
from django.db import transaction

from training_program.models import Program
from infra.utils import prod_logger
from auth.models import Department
from auth.services import PermissionService, DepartmentService


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
            PermissionService.assign_object_permissions(
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

    @staticmethod
    def get_grouped_programs_by_department(user):
        '''group all programs by department'''
        admin_departments = user.groups.filter(
            name__endswith='-管理员').values_list('name', flat=True)
        if not admin_departments:
            return []
        admin_departments = set(
            map(lambda x: x.replace('-管理员', ''), admin_departments))
        top_departments = {x['id']: x['name'] for x in 
            DepartmentService.get_top_level_departments()
            .union(Department.objects.filter(name='大连理工大学'))
            .values('id', 'name')
        }
        programs = Program.objects.filter(
            department__id__in=top_departments.keys()).values(
                'id', 'name', 'department')
        programs_dict = defaultdict(list)
        for program in programs:
            programs_dict[program['department']].append(program)
        is_school_admin = user.is_school_admin
        group_programs = [
            {
                'id': dep,
                'name': top_department_dict[dep],
                'programs': programs_dict[dep]
            } for dep in programs_dict if (
                is_school_admin or
                top_department_dict[dep] in admin_departments)
        ]
        group_programs.sort(key=lambda x: x['id'])
        return group_programs
