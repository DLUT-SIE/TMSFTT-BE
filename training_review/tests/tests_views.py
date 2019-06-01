'''Unit tests for training_review views.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from auth.utils import assign_perm
import training_review.models as treview
import training_record.models as trecord
import training_event.models as tevent


User = get_user_model()


class TestReviewNoteViewSet(APITestCase):
    '''Unit tests for ReviewNote view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)
        cls.group = mommy.make(Group, name="个人权限")
        cls.user.groups.add(cls.group)
        assign_perm('training_record.change_record', cls.group)
        assign_perm('training_review.add_reviewnote', cls.group)
        assign_perm('training_review.view_reviewnote', cls.group)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_review_note(self):
        '''ReviewNote should be created by POST request.'''
        off_campus_event = mommy.make(tevent.OffCampusEvent)
        record = mommy.make(trecord.Record, off_campus_event=off_campus_event)
        group = mommy.make(Group, name="创建权限")
        user = self.user
        user.groups.add(group)
        assign_perm('training_record.change_record', group)
        assign_perm('training_record.change_record', group, record)
        assign_perm('training_review.add_reviewnote', group)
        assign_perm('training_review.view_reviewnote', group)
        content = 'Reviewnote is created.'
        url = reverse('reviewnote-list')
        data = {'record': record.pk,
                'content': content}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(treview.ReviewNote.objects.count(), 1)
        self.assertEqual(treview.ReviewNote.objects.get().user.pk, user.pk)
        self.assertEqual(treview.ReviewNote.objects.get().record.pk, record.pk)
        self.assertEqual(treview.ReviewNote.objects.get().content, content)

    def test_list_review_note(self):
        '''ReviewNotes list should be accessed by GET request.'''
        url = reverse('reviewnote-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
