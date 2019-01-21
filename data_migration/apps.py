'''This is required by Django.'''
from django.apps import AppConfig


class DataMigrationConfig(AppConfig):
    '''This app provides data migration during development.'''
    name = 'data_migration'
