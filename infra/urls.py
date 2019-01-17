'''Register URL routes in auth module.'''
from rest_framework import routers
from rest_framework_jwt.views import verify_jwt_token, obtain_jwt_token
from django.urls import path

import infra.views


router = routers.SimpleRouter()
router.register(r'notification', infra.views.NotificationViewSet)
urlpatterns = router.urls

# JWT authentication views
urlpatterns.extend([
    path('jwt-retrieve/', obtain_jwt_token),
    path('jwt-verify/', verify_jwt_token),
])
