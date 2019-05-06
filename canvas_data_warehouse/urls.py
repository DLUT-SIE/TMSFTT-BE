'''Register URL routes in auth module.'''
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'data-graph', views.CanvasDataViewSet, base_name='data-graph')
urlpatterns = router.urls
