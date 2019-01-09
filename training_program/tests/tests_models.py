from django.test import TestCase

from training_program.models import ProgramCatgegory, ProgramForm, Program


class TestProgramCategory(TestCase):
    def test_str(self):
        name = 'name'
        category = ProgramCatgegory(name=name)

        self.assertEqual(str(category), name)


class TestProgramForm(TestCase):
    def test_str(self):
        name = 'name'
        form = ProgramForm(name=name)

        self.assertEqual(str(form), name)


class TestProgram(TestCase):
    def test_str(self):
        name = 'name'
        program = Program(name=name)

        self.assertEqual(str(program), name)
