from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('contact/', views.contactView, name='contact'),
    path('success/', views.SuccessPage.as_view(), name='success'),
]