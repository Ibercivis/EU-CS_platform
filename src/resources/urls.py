from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('resources', views.resources, name='resources'),
    path('resource/<int:pk>', views.resource, name='resource'),
    path('clearfilters_resources', views.clearFilters, name='clearfilters_resources'),
    path('newResource', views.newResource, name='newResource'),
    path('editResource/<int:pk>', views.editResource, name='editResource'),
    path('saveResourceAjax', views.saveResourceAjax, name='saveResourceAjax'),
    path('approveResource/', views.approveResource, name='approveResource'),
    path('setFeaturedResource/', views.setFeaturedResource, name='setFeaturedResource'),
    path('setTrainingResource/', views.setTrainingResource, name='setTrainingResource'),
    path('deleteResource/<int:pk><int:isTrainingResource>', views.deleteResource, name='deleteResource'),
    path(
        'resourcesAutocompleteSearch/',
        views.resourcesAutocompleteSearch,
        name='resourcesAutocompleteSearch'),
    path(
        'trainingsAutocompleteSearch/',
        views.trainingsAutocompleteSearch,
        name='trainingsAutocompleteSearch'),
    path('get_sub_category/', views.get_sub_category, name='get_sub_category'),
    path('bookmarkResource/', views.bookmarkResource, name='bookmarkResource'),
    path('setHiddenResource/', views.setHiddenResource, name='setHiddenResource'),
    path('allowUserResource/', views.allowUserResource, name='allowUserResource'),
    path('resource_review/<int:pk>', views.resource_review, name='resource_review'),
    url(r'^api/', include('resources.api.urls')),
    path('downloadResources', views.downloadResources, name='downloadResources'),
    path('newTrainingResource', views.newTrainingResource, name='newTrainingResource'),
    path('training_resources', views.training_resources, name='training_resources'),
    path('training_resource/<int:pk>', views.training_resource, name='training_resource'),
    path('editTrainingResource/<int:pk>', views.editTrainingResource, name='editTrainingResource'),
    path('setOwnTraining', views.setOwnTraining, name='setOwnTraining'),
]
