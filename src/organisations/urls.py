from django.urls import path, include
from django.conf.urls import url
from . import views


urlpatterns = [
    path('new_organisation', views.new_organisation, name='new_organisation'),
    path('edit_organisation/<int:pk>', views.edit_organisation, name='edit_organisation'),
    path('organisation/<int:pk>', views.organisation, name='organisation'),
    path('organisations', views.organisations, name='organisations'),
    path('delete_organisation/<int:pk>', views.delete_organisation, name='delete_organisation'),
    path('organisations_autocomplete/', views.organisations_autocomplete, name='organisations_autocomplete'),
    path('allowUserOrganisation/', views.allowUserOrganisation, name='allowUserOrganisation'),
    path("new_ecsa_organisation_membership/<int:pk>", views.newEcsaOrganisationMembership, name="new_ecsa_organisation_membership"),
    path("drop_out_ecsa_organisation_membership/<int:pk>", views.dropOutECSAmembership, name="drop_out_ecsa_organisation_membership"),
    path("claim_ecsa_organisation_payment_revision/<int:pk>", views.claimEcsaPaymentRevision, name="claim_ecsa_organisation_payment_revision"),  
    url(r'^api/', include('organisations.api.urls')),
]