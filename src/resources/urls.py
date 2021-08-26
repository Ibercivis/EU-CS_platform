from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('resources', views.resources, name='resources'),
    path('resource/<int:pk>', views.resource, name='resource'),
    path('clearfilters_resources', views.clearFilters, name='clearfilters_resources'),
    path('new_resource', views.new_resource, name='new_resource'),
    path('editResource/<int:pk>', views.editResource, name='editResource'),
    path('saveResourceAjax', views.saveResourceAjax, name='saveResourceAjax'),
    path('deleteResource/<int:pk><int:isTrainingResource>', views.deleteResource, name='deleteResource'),
    path('resources_autocomplete/', views.resources_autocomplete, name='resources_autocomplete'),
    path('tresources_autocomplete/', views.tresources_autocomplete, name='tresources_autocomplete'),
    path('get_sub_category/', views.get_sub_category, name='get_sub_category'),
    path('setApprovedRsc/', views.setApprovedRsc, name='setApprovedRsc'),
    path('setSavedResource/', views.setSavedResource, name='setSavedResource'),
    path('setHiddenResource/', views.setHiddenResource, name='setHiddenResource'),
    path('setFeaturedResource/', views.setFeaturedResource, name='setFeaturedResource'),
    path('allowUserResource/', views.allowUserResource, name='allowUserResource'),
    path('resource_review/<int:pk>', views.resource_review, name='resource_review'),
    url(r'^api/', include('resources.api.urls')),
    path('downloadResources', views.downloadResources, name='downloadResources'),
    path('new_training_resource', views.new_training_resource, name='new_training_resource'),
    path('training_resources', views.training_resources, name='training_resources'),
    path('training_resource/<int:pk>', views.training_resource, name='training_resource'),
    path('editTrainingResource/<int:pk>', views.editTrainingResource, name='editTrainingResource'),
    path('setTraining', views.setTraining, name='setTraining'),
    path('setOwnTraining', views.setOwnTraining, name='setOwnTraining'),
    path('getResourceKeywordsSelector/', views.getResourceKeywordsSelector, name='getResourceKeywordsSelector'),
    path('getResourceAuthorsSelector/', views.getResourceAuthorsSelector, name='getResourceAuthorsSelector'),
]
