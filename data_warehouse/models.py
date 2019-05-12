'''Models for aggregation data.'''
from django.db import models
from django.contrib.auth import get_user_model

from auth.models import Department


class Ranking(models.Model):
    '''Rank users by different creterions.'''
    RANKING_BY_CAMPUS_TRAINING_HOURS = 0
    RANKING_BY_OFF_CAMPUS_TRAINING_HOURS = 1
    RANKING_BY_TOTAL_TRAINING_HOURS = 2
    RANKING_TYPES = (
        (RANKING_BY_CAMPUS_TRAINING_HOURS, '按校内培训总时长排名'),
        (RANKING_BY_OFF_CAMPUS_TRAINING_HOURS, '按校外培训总时长排名'),
        (RANKING_BY_TOTAL_TRAINING_HOURS, '按培训总时长排名'),
    )

    class Meta:
        verbose_name = '排名'
        verbose_name_plural = '排名'
        unique_together = (('user', 'department', 'ranking_type'),)
        indexes = [
            models.Index(fields=['department', 'ranking_type']),
        ]
        default_permissions = ()

    ranking_type = models.SmallIntegerField(
        verbose_name='排序方式',
        choices=RANKING_TYPES,
    )
    ranking = models.PositiveIntegerField(verbose_name='排名')
    department = models.ForeignKey(
        Department, verbose_name='排名范围', on_delete=models.PROTECT,
        blank=True, null=True)
    user = models.ForeignKey(get_user_model(), verbose_name='用户',
                             on_delete=models.CASCADE)
    value = models.FloatField(verbose_name='值')
