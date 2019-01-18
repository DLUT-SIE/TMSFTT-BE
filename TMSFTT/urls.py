"""TMSFTT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path


API_URLPATTERNS = [
    path('auth/', include('auth.urls')),
    path('training-event/', include('training_event.urls')),
    path('training-review/', include('training_review.urls')),
    path('infra/', include('infra.urls')),
    path('training-program/', include('training_program.urls')),
    path('training-record/', include('training_record.urls'))
]

urlpatterns = [
    path('api/', include(API_URLPATTERNS)),
]

if settings.DEBUG:
    import debug_toolbar
    from rest_framework.documentation import include_docs_urls

    DEBUG_URLPATTERNS = [
        path('admin/', admin.site.urls),
        path('__debug__/', include(debug_toolbar.urls)),
        path('api/', include_docs_urls(title='TMSFTT APIs')),
        path('mock-cas/', include('mock_cas.urls')),
    ]
    urlpatterns.extend(DEBUG_URLPATTERNS)
