'''Register URL routes in auth module.'''
from django.urls import path
from rest_framework import routers
import training_program.views

router = routers.SimpleRouter()
router.register(r'programs', training_program.views.ProgramViewSet)
urlpatterns = [
    path('program-categories/',
         training_program.views.ProgramCategoryView.as_view(),
         name='program-categories'),
] + router.urls
