'''校内活动反馈测试'''
from unittest.mock import (MagicMock, PropertyMock, patch)
from django.test import TestCase
from django.utils.timezone import now
from model_mommy import mommy
from training_record.models import (Record, CampusEventFeedback)
from training_program.models import Program
from training_event.models import CampusEvent
from auth.models import User
from data_warehouse.services.campus_event_feedback_service import (
    CampusEventFeedbackService)
from infra.exceptions import BadRequest


class TestCampusEventFeedbackService(TestCase):
    '''校内活动反馈测试'''
    @patch('django.utils.timezone.now')
    def setUp(self, mock_now):
        self.mock_time = now().replace(year=2010, month=1, day=1)
        mock_now.return_value = self.mock_time
        self.mock_user = mommy.make(
            User,
            first_name='test',
            email='example@test.com'
        )
        self.mock_program = mommy.make(
            Program,
            id=1,
            name='测试项目'
        )
        self.mock_campus_event = mommy.make(
            CampusEvent,
            name='测试项目-测试校内活动',
            program=self.mock_program
        )
        self.mock_record = mommy.make(
            Record,
            campus_event=self.mock_campus_event,
            user=self.mock_user
        )
        self.mock_feedback = mommy.make(
            CampusEventFeedback,
            content='测试反馈',
            record=self.mock_record
        )

    def test_get_feedbacks(self):
        '''Should 根据项目ID得到对应的反馈'''
        mock_user = MagicMock()
        got = CampusEventFeedbackService.get_feedbacks(mock_user, [1])
        self.assertEqual(1, len(got))
        feedback = got[0]
        self.assertEqual(feedback.content, '测试反馈')
        self.assertEqual(feedback.record.user, self.mock_user)
        self.assertEqual(feedback.record.user.first_name, 'test')
        self.assertEqual(
            feedback.record.user.administrative_department,
            self.mock_user.administrative_department
            )
        self.assertEqual(feedback.record.user.email, 'example@test.com')
        self.assertEqual(feedback.record, self.mock_record)
        self.assertEqual(feedback.record.campus_event.program,
                         self.mock_program)
        self.assertEqual(feedback.record.campus_event, self.mock_campus_event)
        self.assertEqual(feedback.create_time, self.mock_time)
        type(mock_user).is_department_admin = PropertyMock(return_value=False)
        type(mock_user).is_school_admin = PropertyMock(return_value=False)
        with self.assertRaisesMessage(BadRequest, '你不是管理员，无权操作。'):
            CampusEventFeedbackService.get_feedbacks(mock_user, [1])
        mock_user = MagicMock()
        type(mock_user).is_school_admin = PropertyMock(return_value=False)
        CampusEventFeedbackService.get_feedbacks(mock_user, [1])
