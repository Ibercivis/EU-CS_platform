from django.urls import path
from . import views

urlpatterns = [
    path('documents', views.documents, name='documents'),
    path('document/<int:pk>', views.document, name='document'),
    path('clearfilters_documents', views.clearFilters, name='clearfilters_documents'),
    path('new_document', views.new_document, name='new_document'),
    path('editDocument/<int:pk>', views.editDocument, name='editDocument'),
    #path('deleteProject/<int:pk>', views.deleteProject, name='deleteProject'),
]

