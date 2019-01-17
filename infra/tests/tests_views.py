'''Unit tests for auth views.'''
from django.contrib.auth import get_user_model
# from django.utils.timezone import now
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import infra.models


User = get_user_model()


class TestNotificationViewSet(APITestCase):
    '''Unit tests for Notification view.'''
    # 一些方法可以先注释掉。也可以改成405就是不允许使用这种方法。
    # def test_create_notification(self):
    #     '''Notification should be created by POST request.'''
    #     url = reverse('notification-list')
    #     sender = mommy.make(User)
    #     recipient = mommy.make(User)
    #     content = "test"
    #     data = {'sender': sender.id, 'recipient': recipient.id,
    #             'content': content}
    #     response = self.client.post
    # (url, data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(infra.models.Notification.objects.count(), 1)
    #     self.assertEqual(infra.models.Notification.objects.get().sender.id,
    #                      sender.id)
    #     self.assertEqual(infra.models.Notification.objects.get().recipient.id,
    #                      recipient.id)

    def test_list_notification(self):
        '''notification list should be accessed by GET request.'''
        url = reverse('notification-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_delete_notification(self):
    #     '''notification should be deleted by DELETE request.'''
    #     notification = mommy.make(infra.models.Notification)
    #     url = reverse('notification-detail', args=(notification.pk,))

    #     response = self.client.delete(url)

    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(infra.models.Notification.objects.count(), 0)

    def test_get_notification(self):
        '''notification should be accessed by GET request.'''
        notification = mommy.make(infra.models.Notification)
        url = reverse('notification-detail', args=(notification.pk,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], notification.id)

    # def test_update_notification(self):
    #     '''notification should be updated by PATCH request.'''
    #     content0 = "123"
    #     content1 = "123123"
    #     notification = mommy.make(infra.models.Notification,
    #                               content=content0)
    #     url = reverse('notification-detail', args=(notification.pk,))
    #     data = {'content': content1}

    #     response = self.client.patch(url, data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('content', response.data)
    #     self.assertEqual(response.data['content'], content1)
