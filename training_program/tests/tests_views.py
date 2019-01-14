'''Unit tests for training_program views.'''
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import training_program.models
import auth.models


class TestProgramCatgegoryViewSet(APITestCase):
    '''Unit tests for ProgramCatgegory view.'''
    def test_create_programcatgegory(self):
        '''ProgramCatgegory should be created by POST request.'''
        url = reverse('programcatgegory-list')
        name = 'programcatgegory'
        data = {'name': name}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_program.models.ProgramCatgegory.
                         objects.count(), 1)
        self.assertEqual(training_program.models.ProgramCatgegory.objects.
                         get().name, name)

    def test_list_programcatgegery(self):
        '''Programcatgegory list should be accessed by GET request.'''
        url = reverse('programcatgegory-list')

        reponse = self.client.get(url)

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)

    def test_delete_programcatgegory(self):
        '''Programcatgegory list should be deleted by DELETE request.'''
        programcatgegory = mommy.make(training_program.models.ProgramCatgegory)
        url = reverse('programcatgegory-detail', args=(programcatgegory.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_program.models.ProgramCatgegory.objects.
                         count(), 0)

    def test_get_programcatgegory(self):
        '''Programcatgegory list should be GET by GET request.'''
        programcatgegory = mommy.make(training_program.models.ProgramCatgegory)
        url = reverse('programcatgegory-detail', args=(programcatgegory.pk,))
        expected_keys = {'id', 'name'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_programcatgegory(self):
        '''Programcatgegory list should be updated by PATCH request.'''
        name0 = 'programcatgegory0'
        name1 = 'programcatgegory1'
        programcatgegory = mommy.make(training_program.models.ProgramCatgegory,
                                      name=name0)
        url = reverse('programcatgegory-detail', args=(programcatgegory.pk, ))
        data = {'name': name1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], name1)


class TestProgramForm(APITestCase):
    '''Unit tests for ProgramForm view.'''
    def test_create_programform(self):
        '''ProgramForm should be created by POST request.'''
        url = reverse('programform-list')
        name = 'programform'
        data = {'name': name}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_program.models.ProgramForm.objects.count(),
                         1)
        self.assertEqual(training_program.models.ProgramForm.objects.get().
                         name, name)

    def test_list_programform(self):
        '''ProgramForm list should be accessed by GET request.'''
        url = reverse('programform-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_programform(self):
        '''ProgramForm list should be deleted by DELETE request.'''
        programform = mommy.make(training_program.models.ProgramForm)
        url = reverse('programform-detail', args=(programform.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_program.models.ProgramForm.objects.count(),
                         0)

    def test_get_programform(self):
        '''ProgramForm list should be GET by GET request.'''
        programform = mommy.make(training_program.models.ProgramForm)
        url = reverse('programform-detail', args=(programform.pk,))
        expected_keys = {'id', 'name'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_programform(self):
        '''ProgramForm list should be updated by PATCH request.'''
        name0 = 'programForm0'
        name1 = 'programForm1'
        programform = mommy.make(training_program.models.ProgramForm,
                                 name=name0)
        url = reverse('programform-detail', args=(programform.pk, ))
        data = {'name': name1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], name1)


class TestProgram(APITestCase):
    '''Unit tests for Program view.'''
    def test_create_program(self):
        '''Program should be created by POST request.'''
        url = reverse('program-list')
        department = mommy.make(auth.models.Department)
        catgegory = mommy.make(training_program.models.ProgramCatgegory)
        form = mommy.make(training_program.models.ProgramForm)
        name = 'program'
        data = {'name': name, 'department': department.id,
                'catgegory': catgegory.id, 'form': [form.id]}

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
        expected_keys = {'id', 'name', 'department', 'catgegory', 'form'}

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
