'''Register URL routes in auth module.'''
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'aggregate-data',
                views.AggregateDataViewSet,
                base_name='aggregate-data')
urlpatterns = router.urls
