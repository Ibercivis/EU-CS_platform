from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
#router.register(r'projects', ProjectViewSet)

urlpatterns = [
    #path('', include(router.urls)),
    path('projects/', views.api_projects, name="api_projects"),
    path('project/<int:pk>', views.api_project_detail, name="api_project_detail"),
]