'''Provide services of training event module.'''
import re
from django.db import transaction
from django.utils.timezone import now
from infra.utils import prod_logger
from infra.exceptions import BadRequest
from training_event.models import CampusEvent, Enrollment, EventCoefficient
from auth.services import PermissionService


class CampusEventService:
    '''Provide services for CampusEvent.'''
    @staticmethod
    def review_campus_event(event, user):
        '''Review a campus event.'''
        event.reviewed = True
        event.save()

        msg = f'用户 {user} 将培训活动 {event} 标记为已审核'
        prod_logger.info(msg)

    @staticmethod
    def create_campus_event(validated_data, coefficients, context=None):
        '''Create a CampusEvent with ObjectPermission.

        Parametsers
        ----------
        validated_data: dict
            This dict should have full information needed to
            create an CampusEvent.
        coefficients: list
            An optional list to provide event_coefficient about
            expert information and participator information.
        context: dict
            An optional dict to provide contextual information. Default: None

        Returns
        -------
        campus_event: CampusEvent
        '''
        if re.search(r'[\'\"%()<>;+-]|script|meta',
                     validated_data['name'], re.I):
            raise BadRequest('活动名称中含有特殊符号或者脚本关键字！')
        with transaction.atomic():
            campus_event = CampusEvent.objects.create(**validated_data)
            PermissionService.assign_object_permissions(
                context['request'].user, campus_event)
            for coefficient in coefficients:
                EventCoefficient.objects.create(campus_event=campus_event,
                                                **coefficient)
            # log the create
            user = context['request'].user
            msg = (f'用户{user}创建了名称为'
                   + f'{campus_event.name}({campus_event.id})的培训活动')
            prod_logger.info(msg)
            return campus_event

    @staticmethod
    def update_campus_event(event, event_data, coefficients, context=None):
        '''Update campus event

        Parameters
        ----------
        event: CampusEvent
            The event we will update.
        event_data: dict
            the event data dict to role-choices update event
        coefficients: list
            the coefficient data for update coefficient
        context: dict
            An optional dict to provide contextual information. Default: None
        Returns
        -------
        event: CampusEvent
        '''
        event_name = event_data.get('name', None)
        if event_name is not None:
            if re.search(r'[\'\"%()<>;+-]|script|meta',
                         event_name, re.I):
                raise BadRequest('活动名称中含有特殊符号或者脚本关键字！')
        with transaction.atomic():
            # update the event coefficient
            for data in coefficients:
                if 'id' in data:
                    data.pop('id')
                try:
                    coefficient_instance = (
                        EventCoefficient.objects.select_for_update().get(
                            campus_event=event.id,
                            role=data['role'])
                        )
                except Exception:
                    raise BadRequest('不存在当前活动系数')

                for attr, value in data.items():
                    setattr(coefficient_instance, attr, value)
                coefficient_instance.save()

            # update the campus event
            for attr, value in event_data.items():
                setattr(event, attr, value)
            # log the update
            user = context['request'].user
            event.save()
            msg = (f'用户{user}修改了名称为'
                   + f'{event.name}({event.id})的培训活动')
            prod_logger.info(msg)
            return event


class EnrollmentService:
    '''Provide services for Enrollment.'''
    @staticmethod
    def create_enrollment(enrollment_data):
        '''Create a enrollment for specific campus event.

        This action is atomic, will fail if there are no more heads counts for
        the campus event or duplicated enrollments are created.

        Parametsers
        ----------
        enrollment_data: dict
            This dict should have full information needed to
            create an Enrollment.

        Returns
        -------
        enrollment: Enrollment
        '''
        with transaction.atomic():
            # Lock the event until the end of the transaction
            event = CampusEvent.objects.select_for_update().get(
                id=enrollment_data['campus_event'].id)
            if now() > event.deadline:
                raise BadRequest('报名时间已过')
            if event.num_enrolled >= event.num_participants:
                raise BadRequest('报名人数已满')

            enrollment = Enrollment.objects.create(**enrollment_data)
            # Update the number of enrolled participants
            event.num_enrolled += 1
            event.save()
            PermissionService.assign_object_permissions(
                enrollment_data['user'], enrollment)

            return enrollment

    @staticmethod
    def delete_enrollment(instance):
        """Provide services for delete enrollments.
        Parameters
        ----------
        instance: enrollment
            删除的enrollment对象
        """
        with transaction.atomic():
            # Lock the event until the end of the transaction
            event = CampusEvent.objects.select_for_update().get(
                id=instance.campus_event_id
            )
            event.num_enrolled -= 1
            event.save()
            instance.delete()

    @staticmethod
    def get_user_enrollment_status(events, user):
        """Provide services for get Enrollment Status.
        Parameters
        ----------
        events: list
            要查询的校内活动的对象列表或者数字列表
        user: number or object
            当然的用户的id或者对象


        Returns
        -------
        result: dict
        key 为活动的编号
        value 活动是否报名，True表示该活动已经报名，False表示活动没有报名
        """
        if events and isinstance(events[0], CampusEvent):
            events = [event.id for event in events]

        enrolled_events = set(Enrollment.objects.filter(
            user=user, campus_event__id__in=events
        ).values_list('campus_event_id', flat=True))

        return {event: event in enrolled_events
                for event in events}

    @staticmethod
    def get_user_enrollment_id(events, user):
        """Provide services for get Enrollment id.
        Parameters
        ----------
        events: list
            要查询的校内活动的对象列表或者数字列表
        user: number or object
            当然的用户的id或者对象


        Returns
        -------
        result: dict
        key 为活动的编号
        value 如果活动报名，value是报名的id，如果活动没有报名，value就是None
        """
        if events and isinstance(events[0], CampusEvent):
            events = [event.id for event in events]

        enrolled_data = dict(Enrollment.objects.filter(
            user=user, campus_event__id__in=events
        ).values_list('campus_event_id', 'id'))

        return {event: enrolled_data[event] if event in enrolled_data else None
                for event in events}

    @staticmethod
    def get_enrollments(event_id, context=None):
        '''get matched enrollments'''
        event = CampusEvent.objects.filter(id=event_id)
        if not event:
            raise BadRequest('未找到对应培训活动')
        event = event[0]
        user = context['user']
        if not user.has_perm('training_event.change_campusevent', event):
            msg = (
                f'用户 {user.username}({user.first_name}) '
                f'查询不具有权限的校内培训活动 {event.id} 的报名信息失败。'
            )
            prod_logger.info(msg)
            raise BadRequest('您无权查询该活动的报名信息')
        return Enrollment.objects.filter(
            campus_event_id=event_id).select_related(
                'user__department', 'campus_event'
            )
