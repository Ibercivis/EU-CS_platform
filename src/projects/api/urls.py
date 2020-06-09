from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects/topic', views.TopicViewSet, basename='topic')
router.register(r'projects/status', views.StatusViewSet, basename='status')

urlpatterns = [
    path('projects/', views.ProjectList.as_view(), name="api_projects"),
    path('projects/<int:pk>', views.ProjectDetail.as_view(), name="api_project_detail"),
]

urlpatterns += router.urls