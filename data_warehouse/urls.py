'''Register URL routes in auth module.'''
from django.urls import path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'aggregate-data',
                views.AggregateDataViewSet,
                base_name='aggregate-data')
urlpatterns = [
    path('log-perform/',
         views.LogPerformView.as_view(),
         name='log-perform'),
] + router.urls
