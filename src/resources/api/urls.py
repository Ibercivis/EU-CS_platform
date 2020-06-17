from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('resources/', views.ResourceList.as_view(), name="api_resources"),
]

urlpatterns += router.urls