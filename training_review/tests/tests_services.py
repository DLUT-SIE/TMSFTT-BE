'''Unit tests for training_program services.'''
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from model_mommy import mommy

from infra.exceptions import BadRequest
from auth.models import Department
from auth.utils import assign_perm
from training_event.models import OffCampusEvent
from training_record.models import Record
from training_review.models import ReviewNote
from training_review.services import ReviewNoteService

User = get_user_model()


class TestReviewNoteService(APITestCase):
    '''Test services provided by ReviewNoteService.'''
    def setUp(self):
        depart = mommy.make(Department, name="创新创业学院")
        group1 = mommy.make(Group, name="个人权限")
        group2 = mommy.make(Group, name="创新创业学院-管理员")
        off_campus_event_instance = mommy.make(OffCampusEvent)
        self.user1 = mommy.make(User, department=depart)
        self.user2 = mommy.make(User)
        self.user1.groups.add(group1)
        self.user2.groups.add(group2)
        self.record = mommy.make(
            Record,
            off_campus_event=off_campus_event_instance,
            user=self.user1)
        assign_perm('training_review.add_reviewnote', group1)
        assign_perm('training_review.view_reviewnote', group1)
        assign_perm('training_review.add_reviewnote', group2)
        assign_perm('training_review.view_reviewnote', group2)

    def test_create_review_note_user(self):
        '''Should create ReviewNote.'''
        data = {'record': self.record, 'content': '*', 'user': self.user1}
        review_note = ReviewNoteService.create_review_note(**data)

        count = ReviewNote.objects.all().count()
        self.assertEqual(count, 1)
        self.assertTrue(self.user1.has_perm('add_reviewnote', review_note))
        self.assertTrue(self.user1.has_perm('view_reviewnote', review_note))
        self.assertTrue(self.user2.has_perm('add_reviewnote', review_note))
        self.assertTrue(self.user2.has_perm('view_reviewnote', review_note))

    def test_create_review_note_admin(self):
        '''Should create ReviewNote.'''
        data = {'record': self.record, 'content': '*', 'user': self.user2}
        review_note = ReviewNoteService.create_review_note(**data)

        count = ReviewNote.objects.all().count()
        self.assertEqual(count, 1)
        self.assertTrue(self.user1.has_perm('add_reviewnote', review_note))
        self.assertTrue(self.user1.has_perm('view_reviewnote', review_note))
        self.assertTrue(self.user2.has_perm('add_reviewnote', review_note))
        self.assertTrue(self.user2.has_perm('view_reviewnote', review_note))

    def test_create_review_note_no_content(self):
        '''Should raise BadRequest if review note's content is None.'''
        content = None
        with self.assertRaisesMessage(
                BadRequest, '审核提示内容不能为空！'):
            ReviewNoteService.create_review_note(
                self.user1, self.record, content)
