'''Register URL routes in training_record module.'''
from rest_framework import routers

import training_record.views


router = routers.SimpleRouter()
router.register(r'records', training_record.views.RecordViewSet)
router.register(r'record-contents', training_record.views.RecordContentViewSet)
router.register(r'record-attachments',
                training_record.views.RecordAttachmentViewSet)
router.register(r'status-change-logs',
                training_record.views.StatusChangeLogViewSet)
router.register(r'campus-event-feedback',
                training_record.views.CampusEventFeedbackViewSet)
router.register(r'records/actions', training_record.views.RecordActionViewSet,
                base_name='record-actions')
urlpatterns = router.urls
