'''Register URL routes in training_record module.'''
from rest_framework import routers

import training_record.views


router = routers.SimpleRouter()
router.register(r'record', auth.views.RecordViewSet)
router.register(r'recordcontent', auth.views.RecordContentViewSet)
router.register(r'recordattachment', auth.views.RecordAttachmentViewSet)
router.register(r'statuschangelog', auth.views.StatusChangeLogViewSet)
urlpatterns = router.urls