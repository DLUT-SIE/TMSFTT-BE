'''Register URL routes in auth module.'''
from rest_framework import routers

import auth.views


router = routers.SimpleRouter()
router.register(r'departments', auth.views.DepartmentViewSet)
router.register(r'user-profiles', auth.views.UserProfileViewSet)
urlpatterns = router.urls
