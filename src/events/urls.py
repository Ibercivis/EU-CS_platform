from django.urls import path, include

from . import views

urlpatterns = [
    path('new_event', views.new_event, name='new_event'),
    path('events', views.events, name='events'),
]