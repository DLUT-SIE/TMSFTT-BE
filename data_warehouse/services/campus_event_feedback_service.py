'''校内培训活动反馈服务'''
from guardian.shortcuts import get_objects_for_user
from training_record.models import CampusEventFeedback
from training_program.models import Program
from infra.exceptions import BadRequest


class CampusEventFeedbackService:
    '''校内活动反馈服务'''
    @staticmethod
    def get_feedbacks(user, program_ids):
        '''获取指定培训项目的培训反馈记录'''
        if user is None or not (user.is_department_admin or user
                                .is_school_admin):
            raise BadRequest('你不是管理员，无权操作。')
        if not CampusEventFeedbackService._check_program_permission(
                user, program_ids):
            raise BadRequest('给定的这些项目中，存在项目不属于您。')
        return CampusEventFeedback.objects.filter(
            record__campus_event__program_id__in=program_ids)

    @staticmethod
    def _check_program_permission(user, program_ids):
        '''检查用户是否拥有这些项目的权限'''
        checked_programs = get_objects_for_user(
            user, 'add_program', Program.objects.filter(id__in=program_ids))
        return len(checked_programs) == len(program_ids)
