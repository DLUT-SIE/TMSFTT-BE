'''Register URL routes in auth module.'''
from rest_framework import routers

import infra.views

# pylint: disable=C0103
router = routers.SimpleRouter()
router.register(r'notifications', infra.views.NotificationViewSet)
router.register(r'notifications/actions',
                infra.views.NotificationActionViewSet,
                basename='notification-actions')
urlpatterns = router.urls
