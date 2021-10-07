from django.urls import path
from . import views

urlpatterns = [
    path('newPlatform/', views.newPlatform, name='newPlatform'),
]
