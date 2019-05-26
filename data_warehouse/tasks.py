'''Celery tasks.'''
import smtplib

from celery import shared_task
from django.db import transaction
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.core.mail import send_mass_mail
from django.contrib.sites.models import Site
from tqdm import tqdm

from auth.services import UserService

from data_warehouse.services import (
    UserRankingService, AggregateDataService,
)
from infra.utils import prod_logger


@shared_task
@transaction.atomic()
def generate_user_rankings():
    '''Generate user rankings.'''
    UserRankingService.generate_user_rankings()


@shared_task
def send_mail_to_inactive_users(skip_users=None):
    '''Send emails to inactive users to encourage them to be active.

    Parameters
    ----------
    skip_users: list
        The ids of the users which should be ignored when sending mails.
        Default: None.
    '''
    if skip_users is None:
        skip_users = []
    skip_users = set(skip_users)
    end_time = now()
    start_time = end_time.replace(year=end_time.year-1)

    def check_user_activity(user):
        '''
        Return whether the user is an active participant along
        with his/her statistics.

        Parameters
        ----------
        user: User
            The user to be checked.

        Return
        ------
        is_active: bool
            Whether the user is an active partcipant.
        statistics: dict
            Detailed statistics about the user.
        '''
        context = {
            'user': user,
            'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
        }
        data = AggregateDataService.personal_summary(context)
        # TODO: Replace with more reasonable settings
        return False, data

    users = UserService.get_full_time_teachers()
    mails = []

    for user in tqdm(users):
        is_active, data = check_user_activity(user)
        if not is_active:
            if user.id in skip_users:
                msg = (
                    f'{user.first_name}({user.username}, {user.email})'
                    f'未满足活跃用户条件，但由于其id出现在忽略用户列表中，'
                    f'将不会向其发送年度报告邮件'
                )
                prod_logger.info(msg)
                continue
            msg = render_to_string(
                'mail_template_for_inactive_user.html',
                context={
                    'site': Site.objects.get_current(),
                    'user': user,
                    'year_of_the_data': start_time.year,
                    'data': data,
                }
            )
            mail = (
                '大连理工大学专任教师教学培训管理系统年度报告',
                msg,
                'TMSFTT',
                user.email,
            )
            mails.append(mail)
    try:
        send_mass_mail(mails, fail_silently=False)
    except smtplib.SMTPException as exc:
        msg = (
            '系统在为每位教师发送年度报告邮件时发生错误，'
            f'部分邮件可能未成功发送，错误信息为：{exc}'
        )
        prod_logger.error(msg)
