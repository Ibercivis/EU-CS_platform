from django.urls import path, include

from . import views

urlpatterns = [
    path('new_project', views.new_project, name='new_project'),
    path('projects', views.projects, name='projects'),
]