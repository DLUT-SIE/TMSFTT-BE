'''Define how our app behave under different configs.'''
from django.apps import AppConfig


class DataGraphConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'data_graph'
    verbose_name = '数据可视化图'
