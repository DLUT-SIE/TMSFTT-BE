'''校内活动反馈测试'''
from unittest.mock import (MagicMock, PropertyMock)
from django.test import TestCase
from model_mommy import mommy
from training_record.models import (Record, CampusEventFeedback)
from training_program.models import Program
from training_event.models import CampusEvent
from data_warehouse.services.campus_event_feedback_service import (
    CampusEventFeedbackService)
from infra.exceptions import BadRequest


class TestCampusEventFeedbackService(TestCase):
    '''校内活动反馈测试'''
    def setUp(self):
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
            campus_event=self.mock_campus_event
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
        self.assertEqual(got[0].content, '测试反馈')

        type(mock_user).is_department_admin = PropertyMock(return_value=False)
        type(mock_user).is_school_admin = PropertyMock(return_value=False)
        with self.assertRaisesMessage(BadRequest, '你不是管理员，无权操作。'):
            CampusEventFeedbackService.get_feedbacks(mock_user, [1])

        mock_user = MagicMock()
        type(mock_user).is_school_admin = PropertyMock(return_value=False)
        CampusEventFeedbackService.get_feedbacks(mock_user, [1])
