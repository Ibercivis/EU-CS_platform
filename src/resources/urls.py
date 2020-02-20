from django.urls import path
from . import views

urlpatterns = [
    path('resources', views.resources, name='resources'),
    path('resource/<int:pk>', views.resource, name='resource'),
    path('clearfilters_resources', views.clearFilters, name='clearfilters_resources'),
    path('new_resource', views.new_resource, name='new_resource'),
    path('editResource/<int:pk>', views.editResource, name='editResource'),
    path('deleteResource/<int:pk>', views.deleteResource, name='deleteResource'),
    path('resources_autocomplete/', views.resources_autocomplete, name='resources_autocomplete'),
]

