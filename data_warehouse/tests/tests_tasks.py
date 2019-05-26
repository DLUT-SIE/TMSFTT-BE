'''Unit tests for data_warehouse celery tasks.'''
from unittest.mock import patch

from model_mommy import mommy
from django.test import TestCase

from auth.models import User
from data_warehouse.tasks import (
    generate_user_rankings, send_mail_to_inactive_users
)


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
    def test_send_mail_to_inactive_users(self, mocked_send_mail):
        '''Should check users' activities and send mails'''
        users = mommy.make(
            User,
            teaching_type='专任教师',
            _quantity=20,
        )
        
        send_mail_to_inactive_users()
        mocked_send_mail.assert_called()
        (mails,), kwargs = mocked_send_mail.call_args
        fail_silently = kwargs['fail_silently']
        self.assertEqual(len(mails), len(users))
        self.assertFalse(fail_silently)
        
    @patch('data_warehouse.tasks.AggregateDataService.personal_summary',
           lambda _: {})
    @patch('data_warehouse.tasks.send_mass_mail')
    def test_send_mail_to_inactive_users_skip_users(self, mocked_send_mail):
        '''Should check users' activities and send mails (skip users)'''
        users = mommy.make(
            User,
            teaching_type='专任教师',
            _quantity=20,
        )
        skip_users = [u.id for u in users[:10]]
        
        send_mail_to_inactive_users(skip_users=skip_users)
        mocked_send_mail.assert_called()
        (mails,), kwargs = mocked_send_mail.call_args
        fail_silently = kwargs['fail_silently']
        self.assertEqual(len(mails), len(users) - len(skip_users))
        self.assertFalse(fail_silently)
        