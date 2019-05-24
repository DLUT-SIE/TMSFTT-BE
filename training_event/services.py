'''Provide services of training event module.'''
from django.db import transaction

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
        with transaction.atomic():
            campus_event = CampusEvent.objects.create(**validated_data)
            PermissionService.assign_object_permissions(
                context['request'].user, campus_event)
            for coefficient in coefficients:
                EventCoefficient.objects.create(campus_event=campus_event,
                                                **coefficient)

            return campus_event


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
