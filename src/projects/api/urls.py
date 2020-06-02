from django.urls import path, include
from projects.api.views import ProjectViewSet
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]