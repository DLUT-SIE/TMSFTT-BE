'''Register URL routes in auth module.'''
from django.urls import path
from . import views

urlpatterns = [
    path('data-graph/', views.DataGraphView.as_view(), name='data-graph'),
    path('data-graph/get_params/',
         views.DataGraphParamView.as_view(),
         name='data-graph-param')
]
