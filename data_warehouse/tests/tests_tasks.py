'''Unit tests for data_warehouse celery tasks.'''
from unittest.mock import patch

from model_mommy import mommy
from django.test import TestCase
from django.utils.timezone import now, localtime

from auth.models import User
from data_warehouse.tasks import (
    generate_user_rankings, send_mail_to_inactive_users,
    send_mail_to_users_with_events_next_day
)
from training_event.models import CampusEvent, Enrollment


class TestTasks(TestCase):
    '''Test celery tests.'''
    @patch('data_warehouse.tasks.UserRankingService')
    def test_generate_user_rankings(self, mocked_service):
        '''Should call UserRankingService.generate_user_rankings().'''
        generate_user_rankings()

        mocked_service.generate_user_rankings.assert_called()

    @patch('data_warehouse.tasks.AggregateDataService.personal_summary',
           lambda _: {})
    @patch('data_warehouse.tasks.send_mass_mail')
    @patch('data_warehouse.tasks.check_user_activity')
    def test_send_mail_to_inactive_users(self, mocked_check, mocked_send_mail):
        '''Should check users' activities and send mails'''
        num_users = 20
        users = mommy.make(
            User,
            teaching_type='专任教师',
            _quantity=num_users,
        )
        mocked_check.side_effect = [(False, {}) for _ in range(num_users)]

        send_mail_to_inactive_users()
        mocked_send_mail.assert_called()
        (mails,), kwargs = mocked_send_mail.call_args
        fail_silently = kwargs['fail_silently']
        self.assertEqual(len(mails), len(users))
        self.assertFalse(fail_silently)

    @patch('data_warehouse.tasks.AggregateDataService.personal_summary',
           lambda _: {})
    @patch('data_warehouse.tasks.send_mass_mail')
    @patch('data_warehouse.tasks.check_user_activity')
    def test_send_mail_to_inactive_users_skip_users(
            self, mocked_check, mocked_send_mail):
        '''Should check users' activities and send mails (skip users)'''
        num_users = 20
        num_active_users = 10
        users = mommy.make(
            User,
            teaching_type='专任教师',
            _quantity=num_users,
        )
        skip_users = [u.id for u in users[:num_active_users]]
        mocked_check.side_effect = [
            (i < num_active_users, {}) for i in range(num_users)]

        send_mail_to_inactive_users(skip_users=skip_users)
        mocked_send_mail.assert_called()
        (mails,), kwargs = mocked_send_mail.call_args
        fail_silently = kwargs['fail_silently']
        self.assertEqual(len(mails), len(users) - len(skip_users))
        self.assertFalse(fail_silently)

    @patch('data_warehouse.tasks.send_mass_mail')
    def test_send_mail_to_users_with_events_next_day(self, mocked_send_mail):
        '''should send mail to users who will attend events tomorrow'''
        current_time = localtime(now())
        event0 = mommy.make(CampusEvent,
                            time=current_time.replace(day=current_time.day+1),
                            name='0')
        event1 = mommy.make(CampusEvent,
                            time=current_time.replace(day=current_time.day+1),
                            name='1')

        for _ in range(10):
            mommy.make(Enrollment, campus_event=event0, user=mommy.make(User))
        for _ in range(10):
            mommy.make(Enrollment, campus_event=event1, user=mommy.make(User))

        send_mail_to_users_with_events_next_day()
        mocked_send_mail.assert_called()
        (mails,), kwargs = mocked_send_mail.call_args
        fail_silently = kwargs['fail_silently']
        self.assertEqual(len(mails), 20)
        self.assertFalse(fail_silently)
