'''Register URL routes in auth module.'''
from rest_framework import routers
import training_program.views

router = routers.SimpleRouter()
router.register(r'program-categories', training_program.views.
                ProgramCategoryViewSet)
router.register(r'program-forms', training_program.views.ProgramFormViewSet)
router.register(r'programs', training_program.views.ProgramViewSet)
urlpatterns = router.urls
