'''Unit tests for training_program views.'''
from django.urls import reverse
from django.contrib.auth import get_user_model
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import training_program.models
import auth.models


User = get_user_model()


class TestProgram(APITestCase):
    '''Unit tests for Program view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_program(self):
        '''Program should be created by POST request.'''
        url = reverse('program-list')
        department = mommy.make(auth.models.Department)

        name = 'program'
        data = {'name': name, 'department': department.id,
                'category': (
                    training_program.models.Program.PROGRAM_CATEGORY_TRAINING)}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_program.models.Program.objects.count(), 1)
        self.assertEqual(training_program.models.Program.objects.get().name,
                         name)

    def test_list_program(self):
        '''Program list should be accessed by GET request.'''
        url = reverse('program-list')

        reponse = self.client.get(url)

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)

    def test_delete_program(self):
        '''Program list should be deleted by DELETE request.'''
        program = mommy.make(training_program.models.Program)
        url = reverse('program-detail', args=(program.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_program.models.Program.objects.count(), 0)

    def test_get_program(self):
        '''Program list should be GET by GET request.'''
        program = mommy.make(training_program.models.Program)
        url = reverse('program-detail', args=(program.pk,))
        expected_keys = {'id', 'name', 'department', 'category',
                         'category_detail'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_program(self):
        '''Program list should be updated by PATCH request.'''
        name0 = 'program0'
        name1 = 'program1'
        program = mommy.make(training_program.models.Program, name=name0)
        url = reverse('program-detail', args=(program.pk, ))
        data = {'name': name1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], name1)


class TestProgramCategoryViewSet(APITestCase):
    '''Unit tests for ProgramCategoryViewSet'''

    def test_program_categories(self):
        '''Should get categories according to request.'''
        user = mommy.make(get_user_model())
        url = reverse('program-categories-list')
        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
