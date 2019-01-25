'''Register URL routes in auth module.'''
from rest_framework import routers
from rest_framework_nested import routers as nested_routers

from auth.urls import router as auth_router
import infra.views

# pylint: disable=C0103
router = routers.SimpleRouter()
router.register(r'notifications', infra.views.NotificationViewSet)
nested_router = nested_routers.NestedSimpleRouter(
    auth_router, r'users', lookup='user')
nested_router.register(
    r'tasks', infra.views.NotificationUserTaskViewSet,
    base_name='notification-user-tasks')
urlpatterns = router.urls + nested_router.urls
