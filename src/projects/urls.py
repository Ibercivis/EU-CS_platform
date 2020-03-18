from django.urls import path, include

from . import views

urlpatterns = [
    path('new_project', views.new_project, name='new_project'),
    path('projects', views.projects, name='projects'),
    path('project/<int:pk>', views.project, name='project'),
    path('editProject/<int:pk>', views.editProject, name='editProject'),
    path('deleteProject/<int:pk>', views.deleteProject, name='deleteProject'),
    path('text_autocomplete/', views.text_autocomplete, name='text_autocomplete'),
    path('host_autocomplete/', views.host_autocomplete, name='host_autocomplete'),
    path('clearfilters/', views.clearFilters, name='clearfilters'),
    path('setFeatured/', views.setFeatured, name='setFeatured'),
    path('setHidden/', views.setHidden, name='setHidden'),
    path('setFollowedProject/', views.setFollowedProject, name='setFollowedProject'),
    path('allowUser/', views.allowUser, name='allowUser'),
]