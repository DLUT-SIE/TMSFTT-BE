'''Unit tests for training_program serializers.'''
from django.test import TestCase

import training_program.serializers as serializers
import training_program.models as models


class TestProgramCategorySerializer(TestCase):
    '''Unit tests for serializer of programcategory.'''
    def test_fields_equal(self):
        '''Serializer should return fields of ProgramCategory correctly.'''
        category = models.ProgramCategory()
        expected_keys = {'id', 'name'}
        keys = set(serializers.ProgramCategorySerializer
                   (category).data.keys())
        self.assertEqual(keys, expected_keys)


class TestProgramFormSerializer(TestCase):
    '''Unit tests for serizalizer of programform.'''
    def test_fields_equal(self):
        '''Serializer should return fields of ProgramForm correctly.'''
        programform = models.ProgramForm()
        expected_keys = {'id', 'name'}
        keys = set(serializers.ProgramFormSerializer(form).data.keys())
        self.assertEqual(keys, expected_keys)


class TestProgramSerializer(TestCase):
    '''Unit tests for serizalizer of program.'''
    def test_fields_equal(self):
        '''Serializer should return fields of Program correctly.'''
        program = models.Program()
        expected_keys = models.Program()
        expected_keys = {'id', 'name', 'department', 'category', 'form'}
        keys = set(serializers.ProgramSerializer(program).data.keys())
        self.assertEqual(keys, expected_keys)
