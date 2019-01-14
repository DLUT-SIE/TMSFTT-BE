'''Unit tests for auth views.'''
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import infra.models


User = get_user_model()


class TestOperationLogViewSet(APITestCase):
    '''Unit tests for OperationLog view.'''
    def test_create_operationlog(self):
        '''operation should be created by POST request.'''
        url = reverse('operationlog-list')

        remote_ip = "100.4.5.6"
        method = 1
        url1 = "http://www.foo.bar"
        referrer = "http://www.baidu.com"
        user_agent = "Mosaic/0.9"
        user = mommy.make(User)
        requester = user.id

        data = {'remote_ip': remote_ip, 'method': method, 'url':
                url1, 'referrer': referrer, 'user_agent': user_agent,
                'requester': requester}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(infra.models.OperationLog.objects.count(), 1)
        # 下面几句话我将name改成了model里面的内容
        self.assertEqual(infra.models.OperationLog.objects.get().remote_ip,
                         remote_ip)
        self.assertEqual(infra.models.OperationLog.objects.get().method,
                         method)
        self.assertEqual(infra.models.OperationLog.objects.get().url, url1)
        self.assertEqual(infra.models.OperationLog.objects.get().referrer,
                         referrer)
        self.assertEqual(infra.models.OperationLog.objects.get().user_agent,
                         user_agent)

    def test_list_operationlog(self):
        '''operationlog list should be accessed by GET request.'''
        url = reverse('operationlog-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_operationlog(self):
        '''operationlog should be deleted by DELETE request.'''
        department = mommy.make(infra.models.OperationLog)
        url = reverse('operationlog-detail', args=(department.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(infra.models.OperationLog.objects.count(), 0)

    def test_get_operationlog(self):
        '''operationlog should be accessed by GET request.'''
        department = mommy.make(infra.models.OperationLog)
        url = reverse('operationlog-detail', args=(department.pk,))
        expected_keys = {'id', 'time', 'remote_ip', 'requester', 'method',
                         'url', 'referrer', 'user_agent'}
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_operationlog(self):
        '''Operationlog should be updated by PATCH request.'''
        method0 = 1
        method1 = 2
        department = mommy.make(infra.models.OperationLog, method=method0)
        url = reverse('operationlog-detail', args=(department.pk,))
        data = {'method': method1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('method', response.data)
        self.assertEqual(response.data['method'], method1)


class TestNotificationViewSet(APITestCase):
    '''Unit tests for Notification view.'''
    def test_create_notification(self):
        '''Notification should be created by POST request.'''
        # notification = mommy.make(infra.models.Notification)
        url = reverse('notification-list')
        user0 = mommy.make(User)
        sender = user0.id
        user1 = mommy.make(User)
        recipient = user1.id
        content = "test"
        read_time = now()
        data = {'sender': sender, 'recipient': recipient,
                'content': content, 'read_time': read_time}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(infra.models.Notification.objects.count(), 1)
        self.assertEqual(infra.models.Notification.objects.get().read_time,
                         read_time)

    def test_list_notification(self):
        '''notification list should be accessed by GET request.'''
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_notification(self):
        '''notification should be deleted by DELETE request.'''
        user_profile = mommy.make(infra.models.Notification)
        url = reverse('notification-detail', args=(user_profile.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(infra.models.Notification.objects.count(), 0)

    def test_get_notification(self):
        '''notification should be accessed by GET request.'''
        notification = mommy.make(infra.models.Notification)
        url = reverse('notification-detail', args=(notification.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], notification.id)

    def test_update_notification(self):
        '''notification should be updated by PATCH request.'''
        content0 = "123"
        content1 = "123123"
        user_profile = mommy.make(infra.models.Notification, content=content0)
        url = reverse('notification-detail', args=(user_profile.pk,))
        data = {'content': content1}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('content', response.data)
        self.assertEqual(response.data['content'], content1)
