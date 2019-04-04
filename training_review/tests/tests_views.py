'''Unit tests for training_review views.'''
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import training_review.models as treview
import training_record.models as trecord
import training_event.models as tevent


User = get_user_model()


class TestReviewNoteViewSet(APITestCase):
    '''Unit tests for ReviewNote view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_review_note(self):
        '''ReviewNote should be created by POST request.'''
        off_campus_event = mommy.make(tevent.OffCampusEvent)
        user = mommy.make(User)
        record = mommy.make(trecord.Record, off_campus_event=off_campus_event)
        field_name = 'reviewnote'
        content = 'Reviewnote is created.'
        url = reverse('reviewnote-list')
        data = {'user': user.pk, 'record': record.pk,
                'field_name': field_name, 'content': content}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(treview.ReviewNote.objects.count(), 1)
        self.assertEqual(treview.ReviewNote.objects.get().user.pk, user.pk)
        self.assertEqual(treview.ReviewNote.objects.get().record.pk,
                         record.pk)
        self.assertEqual(treview.ReviewNote.objects.get().field_name,
                         field_name)
        self.assertEqual(treview.ReviewNote.objects.get().content, content)

    def test_list_review_note(self):
        '''ReviewNotes list should be accessed by GET request.'''
        url = reverse('reviewnote-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_review_note(self):
        '''ReviewNote should be deleted by DELETE request.'''
        off_campus_event = mommy.make(tevent.OffCampusEvent)
        record = mommy.make(trecord.Record, off_campus_event=off_campus_event)
        review_note = mommy.make(treview.ReviewNote, record=record)
        url = reverse('reviewnote-detail', args=(review_note.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(treview.ReviewNote.objects.count(), 0)

    def test_get_review_note(self):
        '''ReviewNote should be accessed by GET request.'''
        off_campus_event = mommy.make(tevent.OffCampusEvent)
        record = mommy.make(trecord.Record, off_campus_event=off_campus_event)
        review_note = mommy.make(treview.ReviewNote, record=record)
        url = reverse('reviewnote-detail', args=(review_note.pk,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], review_note.id)

    def test_update_review_note(self):
        '''ReviewNote should be updated by PATCH request.'''
        field_name0 = 'note0'
        field_name1 = 'note1'
        off_campus_event = mommy.make(tevent.OffCampusEvent)
        record = mommy.make(trecord.Record, off_campus_event=off_campus_event)
        review_note = mommy.make(treview.ReviewNote, field_name=field_name0,
                                 record=record)
        url = reverse('reviewnote-detail', args=(review_note.pk,))
        data = {'field_name': field_name1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('field_name', response.data)
        self.assertEqual(response.data['field_name'], field_name1)
