'''Provide services of training program module.'''
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
    def group_programs_by_department(user):
        '''group all programs by department'''
        is_school_admin = user.is_school_admin
        admin_departments = user.groups.filter(
            name__endswith='管理员').values_list('name', flat=True)
        if not admin_departments.exists():
            return []
        admin_departments = list(
            map(lambda x: x.replace('-管理员', ''), admin_departments))
        top_departments = list(
            DepartmentService.get_top_level_departments()
            .values('id', 'name'))
        dlut_department = Department.objects.get(name='大连理工大学')
        top_departments.append(
            {'id': dlut_department.id, 'name': dlut_department.name})
        programs = list(
            Program.objects.all().values('id', 'name', 'department'))
        group_programs = [
            {
                'id': dep['id'],
                'name': dep['name'],
                'programs': (
                    list(filter(lambda x, dep=dep: (
                        x['department'] == dep['id']), programs)) if (
                            is_school_admin or
                            dep['name'] in admin_departments) else [])
            } for dep in top_departments
        ]
        group_programs.sort(key=lambda x: x['id'])
        return group_programs
