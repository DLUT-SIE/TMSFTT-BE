'''Register URL routes in training_event module.'''
from rest_framework import routers
from django.urls import path

import training_event.views


router = routers.SimpleRouter()
router.register(r'campus-events', training_event.views.CampusEventViewSet)
router.register(r'off-campus-events',
                training_event.views.OffCampusEventViewSet)
router.register(r'enrollments', training_event.views.EnrollmentViewSet)
router.register(r'enrollments/actions', training_event.views.EnrollmentViewSet,
                base_name='enrollments-actions')
urlpatterns = router.urls
urlpatterns.extend([
    path('download/workload',
         training_event.views.WorkloadFileDownloadView.as_view(),
         name='download-workload'),
])
