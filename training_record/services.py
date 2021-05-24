'''Provide services of training record module.'''
import tempfile
import smtplib
import re
import xlrd

from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from django.utils.timezone import now, localtime
from django.core.mail import send_mass_mail

from auth.services import PermissionService
from infra.utils import prod_logger
from infra.services import (
    NotificationService,
    SOAPMSGService,
    SOAPSMSService)
from infra.exceptions import BadRequest
from training_record.models import (
    Record, RecordContent, RecordAttachment,
    CampusEventFeedback, StatusChangeLog
)
from training_record.utils import is_admin_allowed_operating
from training_event.models import OffCampusEvent, CampusEvent, EventCoefficient
from tiny_url.services import TinyURLService


User = get_user_model()


class RecordService:
    '''Provide services for Record.'''
    @staticmethod
    def create_off_campus_record_from_raw_data(data):
        '''Create a training record of off-campus training event.

        Parameters
        ----------
        data: dict
                off_campus_event: dict
                    This dict should have full information needed to create an
                    OffCampusEvent.
                user: User
                    The user of which the record is related to.
                contents: list of dict
                    Every dict of this list should have full information needed
                    to create a RecordContent.
                attachments: list of InMemoryFile
                role: number
                    The role of the user.
        Returns
        -------
        record: Record
        '''
        try:
            off_campus_event = data['off_campus_event']
            user = data['user']
            contents = data['contents']
            attachments = data.get('attachments', [])
            role = data['role']
        except Exception:
            raise BadRequest('数据格式无效')

        if re.search(r'[\'\"%()<>;+-]|script|meta',
                     off_campus_event['name'], re.I):
            raise BadRequest('培训名称中含有特殊符号或者脚本关键字！')

        with transaction.atomic():
            off_campus_event = OffCampusEvent.objects.create(
                **off_campus_event,
            )

            event_coefficient = EventCoefficient.objects.create(
                role=role, coefficient=0,
                off_campus_event=off_campus_event)

            record = Record.objects.create(
                off_campus_event=off_campus_event,
                user=user,
                event_coefficient=event_coefficient,
            )
            PermissionService.assign_object_permissions(user, record)

            for content in contents:
                record_content = RecordContent.objects.create(
                    record=record,
                    **content
                )
                PermissionService.assign_object_permissions(
                    user, record_content)

            for attachment in attachments:
                record_attachment = RecordAttachment.objects.create(
                    record=record,
                    path=attachment,
                )
                PermissionService.assign_object_permissions(
                    user, record_attachment)
            msg = (f'用户{user}创建了其参加'
                   + f'{off_campus_event.name}'
                   + f'({off_campus_event.id})活动的培训记录')
            prod_logger.info(msg)
        return record

    # pylint: disable=invalid-name
    # pylint: disable=redefined-builtin
    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    @staticmethod
    def update_off_campus_record_from_raw_data(
            record, data, context=None):
        '''Update the off-campus record

        Parameters
        ----------
        data: dict
                off_campus_event: dict
                    This dict should have full information needed to update an
                    OffCampusEvent.
                user: User
                    The user of which the record is related to.
                contents: list of dict
                    Every dict of this list should have full information needed
                    to create a RecordContent.
                attachments: list of InMemoryFile
                role: number
                    The role of the user.

        context:dict
            this dict should have information of user who sent request
        Returns
        -------
        record: Record
        '''
        try:
            off_campus_event = data['off_campus_event']
            user = data['user']
            contents = data['contents']
            attachments = data.get('attachments', [])
            role = data['role']
        except Exception:
            raise BadRequest('数据格式无效')

        if re.search(r'[\'\"%()<>;+-]|script|meta',
                     off_campus_event['name'], re.I):
            raise BadRequest('培训名称中含有特殊符号或者脚本关键字！')

        off_campus_event_data = off_campus_event

        with transaction.atomic():
            # get the record to be updated
            try:
                record = Record.objects.select_for_update().get(
                    id=record.id)
            except Exception:
                raise BadRequest('校外培训记录无效')

            # update the offCampusEvent
            off_campus_event_instance = record.off_campus_event

            if 'id' in off_campus_event_data:
                off_campus_event_data.pop('id')
            for key, val in off_campus_event_data.items():
                setattr(off_campus_event_instance, key, val)
            off_campus_event_instance.save()

            record.event_coefficient.role = role
            record.event_coefficient.save()

            # add attachments
            for attachment in attachments:
                record_attachment = RecordAttachment.objects.create(
                    record=record,
                    path=attachment,
                )
                PermissionService.assign_object_permissions(
                    user, record_attachment)

            if RecordAttachment.objects.filter(record=record).count() > 3:
                raise BadRequest('最多允许上传3个附件')

            # Remove all contents and create new, whether
            # they have been changed or not.
            record.contents.all().delete()
            for content in contents:
                record_content = RecordContent.objects.create(
                    record=record,
                    **content
                )
                PermissionService.assign_object_permissions(
                    user, record_content)
            # reset status
            pre_status = record.status
            record.status = Record.STATUS_SUBMITTED
            post_status = record.status
            record.save()
            StatusChangeLog.objects.create(
                record=record,
                pre_status=pre_status,
                post_status=post_status,
                time=now(),
                user=user,)

            request_user = context['request'].user
            msg = (f'用户{request_user}修改了用户{user}参加'
                   + f'{off_campus_event_instance.name}'
                   + f'({off_campus_event_instance.id})活动的培训记录')
            prod_logger.info(msg)
        return record

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    @staticmethod
    def create_campus_records_from_excel(file, context):
        '''Create training records of campus training event.

        Parameters
        ----------
        file: InMemoryFile
            This file should have full information needed to create a
            Record of campus-event.
            The first line should be the id of each campus-event.
            For each campus-event, the id of its participant should be
            below its id.

        Returns
        -------
        count of records
        '''

        records = set()
        users = set()
        mails = []  # mail: 邮件内容
        smses = []  # sms: 短信内容
        msges = []  # msg_info: 门户消息
        base_url = 'http://ctfdpeixun.dlut.edu.cn/tiny/'

        try:
            # get information
            tup = tempfile.mkstemp()
            with open(tup[0], 'wb') as work_book:
                work_book.write(file)
            # open excel and get the first sheet
            sheet = xlrd.open_workbook(tup[1]).sheet_by_index(0)

            with transaction.atomic():
                # get event from sheet
                event_id = int(sheet.cell(0, 1).value)
                try:
                    campus_event = CampusEvent.objects.get(pk=event_id)
                except Exception:
                    raise BadRequest('编号为{}的活动不存在'.format(event_id))

                if not campus_event.reviewed:
                    raise BadRequest('培训活动还未经学校管理员审核')

                admin = context['user']
                if not admin.has_perm(
                        'training_event.change_campusevent', campus_event):
                    raise BadRequest('您没有为对应培训活动创建培训记录的权限')

                # get coefficient from sheet
                coefficients = {
                    x.get_role_display(): x
                    for x in EventCoefficient.objects.filter(
                        campus_event_id=event_id)
                }

                # process the info of users
                for index in range(3, sheet.nrows):
                    isSigned = sheet.cell(index, 8).value
                    if not isSigned:
                        continue
                    val = sheet.cell(index, 2).value
                    if isinstance(val, str):
                        username = val
                    else:
                        username = f'{int(val)}'

                    try:
                        user = User.objects.get(username=username)
                    except Exception:
                        raise BadRequest('第{}行，用户名为{}的用户不存在'.format(
                            index + 1, username))

                    if user in users:
                        raise BadRequest('第{}行，用户名为{}的用户重复'.format(
                            index + 1, username))
                    users.add(user)

                    role_str = sheet.cell(index, 7).value
                    event_coefficient = coefficients.get(role_str, None)
                    if event_coefficient is None:
                        raise BadRequest('第{}行，不存在的参与形式'.format(
                            index + 1))
                    try:
                        record = Record.objects.create(
                            campus_event=campus_event, user=user,
                            status=Record.STATUS_FEEDBACK_REQUIRED,
                            event_coefficient=event_coefficient)
                    except IntegrityError:
                        raise BadRequest('第{}行，已经存在用户名为{}的用户参加该活动的培训记录'.format(
                            index + 1, username))

                    PermissionService.assign_object_permissions(user, record)
                    records.add(record)

                    msg = (f'管理员{admin}创建了用户{user}参加'
                           + f'{campus_event.name}({campus_event.id})活动的培训记录')
                    prod_logger.info(msg)

                    msg = '您有一条新的校内培训记录'
                    NotificationService.send_system_notification(user, msg)

                    tiny_url = TinyURLService.generate_tiny_url(
                        'records/{}'.format(record.id))
                    url = base_url + tiny_url.short_url
                    msg = ('老师，您好！您参加{}活动的培训记录已录入教学培训管理系统，'
                           '提醒您及时登录系统填写培训反馈。'
                           '谢谢！'
                           '网页链接: {}').format(campus_event.name, url)
                    mail = (
                        '培训记录已录入',
                        msg,
                        'TMSFTT',
                        [user.email],
                    )
                    mails.append(mail)
                    sms = {
                        'user_phone_number': user.cell_phone_number,
                        'sms_info': msg,
                    }
                    smses.append(sms)
                    msg_info = {
                        'user_username': user.username,
                        'msg_title': '培训活动提醒',
                        'msg_info': msg,
                    }
                    msges.append(msg_info)

        except Exception as exc:
            if isinstance(exc, (BadRequest, IntegrityError)):
                raise
            raise BadRequest('无效的表格')

        try:
            send_mass_mail(mails, fail_silently=False)
        except smtplib.SMTPException as exc:
            msg = (
                '系统在提醒教师参加活动时发生错误，'
                f'部分邮件可能未成功发送，错误信息为：{exc}'
            )
            prod_logger.error(msg)

        try:
            SOAPSMSService.send_sms(smses)
        except Exception as exc:
            msg = (
                '系统在提醒教师参加活动时发生错误，'
                f'部分短信可能未成功发送，错误信息为：{exc}'
            )
            prod_logger.error(msg)

        try:
            SOAPMSGService.send_msg(msges)
        except Exception as exc:
            msg = (
                '系统在提醒教师参加活动时发生错误，'
                f'部分门户信息可能未成功发送，错误信息为：{exc}'
            )
            prod_logger.error(msg)

        return len(records)

    @staticmethod
    def department_admin_review(record_id, is_approved, user):
        '''Department admin review the off-campus training record.

        This action is atomic, will fail if there is no enough permissions for
        admins to change record status or no such record.

        Parameters
        ----------
        record_id: number
            This parameter represents which record's status should be changed.
        is_approved: Boolean
            This parameter represents whether the record is passed or not.
        user: number
            This parameter represents who reviewed the record.

        Returns
        -------
        record: Record
        '''
        with transaction.atomic():
            record = (Record
                      .objects
                      .select_for_update()
                      .filter(pk=record_id, campus_event__isnull=True))
            if not record:
                raise BadRequest('无此培训记录')
            record = record[0]
            if not is_admin_allowed_operating(user, record):
                raise BadRequest('无权更改')
            pre_status = record.status
            if is_approved:
                record.status = Record.STATUS_DEPARTMENT_ADMIN_APPROVED
            else:
                record.status = Record.STATUS_DEPARTMENT_ADMIN_REJECTED
            post_status = record.status
            StatusChangeLog.objects.create(
                record=record,
                pre_status=pre_status,
                post_status=post_status,
                time=now(),
                user=user)
            record.save()
            msg = (
                '您有一条培训记录已被院系管理员审核，'
                f'当前状态：{record.get_status_display()}'
            )
            NotificationService.send_system_notification(record.user, msg)

            if is_approved:
                school_admin = User.objects.get(id=10977)
                msg = (
                    '有新的培训记录需要审核'
                )
                NotificationService.send_system_notification(school_admin, msg)
        return record

    @staticmethod
    def school_admin_review(record_id, is_approved, user):
        '''School admin review the off-campus training record.

        This action is atomic, will fail if there is no enough permissions for
        admins to change record status or no such record.

        Parameters
        ----------
        record_id: number
            This parameter represents which record's status should be changed.
        is_approved: Boolean
            This parameter represents whether the record is passed or not.
        user: number
            This parameter represents who reviewed the record.

        Returns
        -------
        record: Record
        '''
        with transaction.atomic():
            record = (Record
                      .objects
                      .select_for_update()
                      .filter(pk=record_id, campus_event__isnull=True))
            if not record:
                raise BadRequest('无此培训记录')
            record = record[0]
            if not is_admin_allowed_operating(user, record):
                raise BadRequest('无权更改')
            pre_status = record.status
            if is_approved:
                record.status = Record.STATUS_SCHOOL_ADMIN_APPROVED
            else:
                record.status = Record.STATUS_SCHOOL_ADMIN_REJECTED
            post_status = record.status
            StatusChangeLog.objects.create(
                record=record,
                pre_status=pre_status,
                post_status=post_status,
                time=now(),
                user=user)
            record.save()
            msg = (
                '您有一条培训记录已被学校管理员审核，'
                f'当前状态：{record.get_status_display()}'
            )
            NotificationService.send_system_notification(record.user, msg)
        return record

    @staticmethod
    def close_record(record_id, user):
        '''School admin close the off-campus training record.

        This action is atomic, will fail if there is no enough permissions for
        admins to close record or no such record.

        Parameters
        ----------
        record_id: number
            This parameter represents which record should be closed.
        user: number
            This parameter represents who closed the record.

        Returns
        -------
        record: Record
        '''
        with transaction.atomic():
            record = (Record
                      .objects
                      .select_for_update()
                      .filter(pk=record_id))
            if not record:
                raise BadRequest('无此培训记录')
            record = record[0]
            pre_status = record.status
            record.status = Record.STATUS_CLOSED
            post_status = record.status
            StatusChangeLog.objects.create(
                record=record,
                pre_status=pre_status,
                post_status=post_status,
                time=now(),
                user=user)
            record.save()
            msg = '您有一条培训记录已被关闭，该记录将无法再进行后续流程。'
            NotificationService.send_system_notification(record.user, msg)
        return record

    @staticmethod
    def get_number_of_records_without_feedback(user):
        '''Get the number of records which requiring feedback'''
        count = Record.objects.filter(
            user=user, off_campus_event__isnull=True, feedback=None).count()
        return count

    @staticmethod
    def get_recent_events_of_import_records():
        '''Get the recent events which has records.'''
        events = set()
        current_time = localtime(now())
        records = Record.objects.filter(
            create_time__gte=current_time.replace(hour=0, minute=0, second=0),
            off_campus_event__isnull=True,
        )
        for record in records:
            events.add(record.campus_event)

        return list(events)


class CampusEventFeedbackService:
    '''Provide services for CampusEventFeedback.'''
    @staticmethod
    def create_feedback(data, context):
        '''Create feedback for campus-event and update the status
        of the related-record to be STATUS_FEEDBACK_SUBMITTED.'''
        record = data['record']
        content = data['content']
        inspiring_level = data['inspiring_level']
        inspiring_less_reason = data.get('inspiring_less_reason', '')
        profits = data['profits']
        profit_other = data.get('profit_other', '')
        willingness_level = data['willingness_level']

        related_record = Record.objects.get(pk=record.id)
        with transaction.atomic():
            feedback = CampusEventFeedback.objects.create(
                record=record,
                content=content,
                inspiring_level=inspiring_level,
                inspiring_less_reason=inspiring_less_reason,
                profits=profits,
                profit_other=profit_other,
                willingness_level=willingness_level)
            related_record.status = Record.STATUS_FEEDBACK_SUBMITTED
            related_record.save()

            user = context['request'].user
            msg = (f'用户{user}提交了用户{record.user}参加'
                   + f'{record.campus_event.name}'
                   + f'({record.campus_event.id})活动的培训反馈')
            prod_logger.info(msg)
        return feedback
