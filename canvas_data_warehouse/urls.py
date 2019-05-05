'''Register URL routes in auth module.'''
from django.urls import path
from . import views

urlpatterns = [
    path('data-graph/',
         views.CanvasDataViewSet.as_view({'get': 'get_canvas_data'}),
         name='data-graph'),
    path('data-graph/get-params/',
         views.DataGraphParamViewSet.as_view({'get': 'get_param'}),
         name='data-graph-param')
]
