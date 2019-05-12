'''Celery tasks.'''
from celery import shared_task
from django.db import transaction

from data_warehouse.services import UserRankingService


@shared_task
@transaction.atomic()
def generate_user_rankings():
    '''Generate user rankings.'''
    UserRankingService.generate_user_rankings()
