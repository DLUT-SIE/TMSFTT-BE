'''Register URL routes in training_review module.'''
from rest_framework import routers

import training_review.views


router = routers.SimpleRouter()
router.register(r'review-notes', training_review.views.ReviewNoteViewSet)
urlpatterns = router.urls
