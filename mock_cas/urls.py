'''Register URL routes in mock_cas module.'''
from django.urls import path

import mock_cas.views


urlpatterns = [
    # CAS clients redirect their users to this route to perform login action.
    path('login/', mock_cas.views.MockedCASLoginView.as_view()),
    # CAS clients talk to this route to verify the ticket issued by CAS server.
    path('proxyValidate/', mock_cas.views.MockedCASValidateView.as_view()),
]
