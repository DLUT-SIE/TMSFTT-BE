'''Unit tests for training_program views.'''
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import training_program.models
import auth.models


class TestProgramCategoryViewSet(APITestCase):
    '''Unit tests for ProgramCategory view.'''
    def test_create_program_category(self):
        '''ProgramCategory should be created by POST request.'''
        url = reverse('programcategory-list')
        name = 'category'
        data = {'name': name}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            training_program.models.ProgramCategory.objects.count(), 1)
        self.assertEqual(
            training_program.models.ProgramCategory.objects.get().name, name)

    def test_list_program_catgegery(self):
        '''Programcategory list should be accessed by GET request.'''
        url = reverse('programcategory-list')

        reponse = self.client.get(url)

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)

    def test_delete_program_category(self):
        '''Programcategory list should be deleted by DELETE request.'''
        category = mommy.make(training_program.models.ProgramCategory)
        url = reverse('programcategory-detail', args=(category.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            training_program.models.ProgramCategory.objects.count(), 0)

    def test_get_program_category(self):
        '''Programcategory list should be GET by GET request.'''
        category = mommy.make(training_program.models.ProgramCategory)
        url = reverse('programcategory-detail', args=(category.pk,))
        expected_keys = {'id', 'name'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_program_category(self):
        '''Programcategory list should be updated by PATCH request.'''
        name0 = 'category0'
        name1 = 'category1'
        category = mommy.make(training_program.models.ProgramCategory,
                              name=name0)
        url = reverse('programcategory-detail', args=(category.pk, ))
        data = {'name': name1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], name1)


class TestProgramForm(APITestCase):
    '''Unit tests for ProgramForm view.'''
    def test_create_program_form(self):
        '''ProgramForm should be created by POST request.'''
        url = reverse('programform-list')
        name = 'form'
        data = {'name': name}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_program.models.ProgramForm.objects.count(),
                         1)
        self.assertEqual(
            training_program.models.ProgramForm.objects.get().name, name)

    def test_list_program_form(self):
        '''ProgramForm list should be accessed by GET request.'''
        url = reverse('programform-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_program_form(self):
        '''ProgramForm list should be deleted by DELETE request.'''
        form = mommy.make(training_program.models.ProgramForm)
        url = reverse('programform-detail', args=(form.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_program.models.ProgramForm.objects.count(),
                         0)

    def test_get_program_form(self):
        '''ProgramForm list should be GET by GET request.'''
        form = mommy.make(training_program.models.ProgramForm)
        url = reverse('programform-detail', args=(form.pk,))
        expected_keys = {'id', 'name'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_program_form(self):
        '''ProgramForm list should be updated by PATCH request.'''
        name0 = 'form0'
        name1 = 'form1'
        form = mommy.make(training_program.models.ProgramForm,
                          name=name0)
        url = reverse('programform-detail', args=(form.pk,))
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
        category = mommy.make(training_program.models.ProgramCategory)
        form = mommy.make(training_program.models.ProgramForm)
        name = 'program'
        data = {'name': name, 'department': department.id,
                'category': category.id, 'form': [form.id]}

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
        expected_keys = {'id', 'name', 'department', 'category', 'form'}

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
