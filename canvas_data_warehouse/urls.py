'''Register URL routes in auth module.'''
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'canvas-data',
                views.CanvasDataViewSet,
                base_name='canvas-data')
urlpatterns = router.urls
