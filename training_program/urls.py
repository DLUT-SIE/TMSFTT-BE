'''Register URL routes in auth module.'''
from rest_framework import routers
import training_program.views

router = routers.SimpleRouter()
router.register(r'programs', training_program.views.ProgramViewSet)
router.register(r'program-categories',
                training_program.views.ProgramCategoryViewSet,
                base_name='program-categories')
urlpatterns = router.urls
