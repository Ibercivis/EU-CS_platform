from django.urls import path
from . import views

urlpatterns = [
    path('documents', views.documents, name='documents'),
    path('new_document', views.new_document, name='new_document'),
]

