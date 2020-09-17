from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'organisations/type', views.OrganisationTypeViewSet, basename='organisation_type')

urlpatterns = [
    path('organisations/', views.OrganisationList.as_view(), name="api_organisations"),
    path('organisations/<int:pk>', views.OrganisationDetail.as_view(), name="api_organisation_detail"),
]

urlpatterns += router.urls