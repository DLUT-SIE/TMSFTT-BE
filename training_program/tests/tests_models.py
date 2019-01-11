'''Unit tests for training_program models.'''
from django.test import TestCase

from training_program.models import ProgramCatgegory, ProgramForm, Program


class TestProgramCategory(TestCase):
    '''Unit tests for model ProgramCategory.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'
        category = ProgramCatgegory(name=name)

        self.assertEqual(str(category), name)


class TestProgramForm(TestCase):
    '''Unit tests for model ProgramForm.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'
        form = ProgramForm(name=name)

        self.assertEqual(str(form), name)


class TestProgram(TestCase):
    '''Unit tests for model Program.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'
        program = Program(name=name)
        self.assertEqual(str(program), name)
