from django.urls import path, include
from . import views

urlpatterns = [
    path('new_organisation', views.new_organisation, name='new_organisation'),
    path('organisation/<int:pk>', views.organisation, name='organisation'),
]