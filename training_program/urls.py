'''Register URL routes in auth module.'''
from rest_framework import routers
import training_program.views

router = routers.SimpleRouter()
router.register(r'programcatgegory', training_program.views.
                ProgramCatgegoryViewSet)
router.register(r'programform', training_program.views.ProgramFormViewSet)
router.register(r'program', training_program.views.ProgramViewSet)
urlpatterns = router.urls
