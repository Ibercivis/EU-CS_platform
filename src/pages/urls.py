from . import views
from django.urls import path
from django.urls import include

urlpatterns = [
    path('p/<slug:slug>', views.page, name='page'),
]