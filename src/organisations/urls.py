from django.urls import path, include
from . import views

urlpatterns = [
    path('new_organisation', views.new_organisation, name='new_organisation'),
    path('edit_organisation/<int:pk>', views.edit_organisation, name='edit_organisation'),
    path('organisation/<int:pk>', views.organisation, name='organisation'),
    path('organisations', views.organisations, name='organisations'),
]