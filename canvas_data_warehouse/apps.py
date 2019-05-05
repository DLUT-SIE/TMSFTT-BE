'''Define how our app behave under different configs.'''
from django.apps import AppConfig


class CanvasDataWarehouseConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'canvas_data_warehouse'
    verbose_name = '画布数据仓库'
