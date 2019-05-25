'''Unit tests for canvas options services.'''
from django.test import TestCase

from data_warehouse.services.canvas_options_service import (
    CanvasOptionsService
)


class TestCanvasOptionsService(TestCase):
    '''Test services provided by CanvasOptionsService.'''

    def test_tuple_to_dict_list(self):
        '''test tuple_to_dict_list function'''
        tuple_list = [(1, 1, 1)]
        dict_list = CanvasOptionsService.tuple_to_dict_list(tuple_list)
        self.assertEqual(dict_list[0]['type'], 1)
        self.assertEqual(dict_list[0]['name'], 1)
        self.assertEqual(dict_list[0]['key'], 1)

    def test_get_canvas_options(self):
        '''test get_canvas_options function'''
        canvas_option = CanvasOptionsService.get_canvas_options()
        self.assertEqual(len(canvas_option), 4)
