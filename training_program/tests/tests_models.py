'''Unit tests for training_program models.'''
from django.test import TestCase

from training_program.models import Program


class TestProgram(TestCase):
    '''Unit tests for model Program.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'
        program = Program(name=name)
        self.assertEqual(str(program), name)
