from django.urls import path, include

from . import views

urlpatterns = [
    path('new_event', views.new_event, name='new_event'),
    path('events', views.events, name='events'),
    path('editEvent/<int:pk>', views.editEvent, name='editEvent'),
    path('deleteEvent/<int:pk>', views.deleteEvent, name='deleteEvent'),
    path('setFeaturedEvent/', views.setFeaturedEvent, name='setFeaturedEvent'),
    path('setApprovedEvent/', views.setApprovedEvent, name='setApprovedEvent'),
]