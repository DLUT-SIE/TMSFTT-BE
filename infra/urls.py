'''Register URL routes in auth module.'''
from rest_framework import routers

import infra.views


router = routers.SimpleRouter()
router.register(r'notifications', infra.views.NotificationViewSet)
urlpatterns = router.urls
