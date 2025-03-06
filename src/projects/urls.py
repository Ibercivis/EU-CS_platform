
""" Urls for projects app """
from django.urls import path, include, re_path
from . import views


urlpatterns = [
    path('newProject', views.newProject, name='newProject'),
    path('editProject/<int:pk>', views.editProject, name='editProject'),
    path('saveProjectAjax', views.saveProjectAjax, name='saveProjectAjax'),
    path('projects', views.projects, name='projects'),
    path('projects_stats', views.projects_stats, name='projects_stats'),
    path('getProjectTranslation/', views.getProjectTranslation,
         name='getProjectTranslation'),
    path('submitProjectTranslation/', views.submitProjectTranslation,
         name='submitProjectTransalation'),
    path('project/<int:pk>', views.project, name='project'),
    path('deleteProject/<int:pk>', views.deleteProject, name='deleteProject'),
    path('translateProject/<int:pk>',
         views.translateProject, name='translateProject'),
    path('projectsAutocompleteSearch/', views.projectsAutocompleteSearch,
         name='projectsAutocompleteSearch'),
    path('clearfilters/', views.clearFilters, name='clearfilters'),
    path('setApproved/', views.setApproved, name='setApproved'),
    path('setHidden/', views.setHidden, name='setHidden'),
    path('setFeatured/', views.setFeatured, name='setFeatured'),
    path('setFollowedProject/', views.setFollowedProject,
         name='setFollowedProject'),
    path('allowUser/', views.allowUser, name='allowUser'),
    path('project_review/<int:pk>', views.project_review, name='project_review'),
    path('likeProjectAjax', views.likeProjectAjax, name='likeProjectAjax'),
    path('followProjectAjax', views.followProjectAjax, name='followProjectAjax'),
    re_path(r'^api/', include('projects.api.urls')),
    path('downloadProjects', views.downloadProjects, name='downloadProjects'),
    path('generateProjectStatsAjax', views.generateProjectStatsAjax,name='generateProjectStatsAjax'),
]
