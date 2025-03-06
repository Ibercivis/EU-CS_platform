from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('new_organisation', views.new_organisation, name='new_organisation'),
    path('edit_organisation/<int:pk>', views.edit_organisation, name='edit_organisation'),
    path('organisation/<int:pk>', views.organisation, name='organisation'),
    path('organisations', views.organisations, name='organisations'),
    path('delete_organisation/<int:pk>', views.delete_organisation, name='delete_organisation'),
    path(
        'organisationsAutocompleteSearch/',
        views.organisationsAutocompleteSearch,
        name='organisationsAutocompleteSearch'),
    path('allowUserOrganisation/', views.allowUserOrganisation, name='allowUserOrganisation'),
    re_path(r'^api/', include('organisations.api.urls')),
]
