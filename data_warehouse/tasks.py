'''Celery tasks.'''
from celery import shared_task
from django.db import transaction

from data_warehouse.services.user_ranking_service import UserRankingService


@shared_task
@transaction.atomic()
def generate_user_rankings():
    '''Generate user rankings.'''
    UserRankingService.generate_user_rankings()
