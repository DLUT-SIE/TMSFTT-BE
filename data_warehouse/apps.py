'''Define how our app behave under different configs.'''
from django.apps import AppConfig


class CanvasDataWarehouseConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'data_warehouse'
    verbose_name = '数据仓库'
