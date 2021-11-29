from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects/topic', views.TopicViewSet, basename='topic')
router.register(r'projects/status', views.StatusViewSet, basename='status')
router.register(r'projects/hastag', views.HasTagViewSet, basename='hastag')
router.register(r'projects/participationTask', views.ParticipationTaskViewSet, basename='participationTask')
router.register(r'projects/geographicExtend', views.GeographicExtendViewSet, basename='geographicExtend')

urlpatterns = [
    path('projects/', views.ProjectList.as_view(), name="api_projects"),
    path('project/<int:pk>', views.ProjectDetail.as_view(), name="api_project_detail"),
    path('projectCreate/', views.ProjectCreate.as_view(), name="api_project_create"),
    path('projectTranslate/<int:pk>', views.ProjectTranslate.as_view(), name="project_translate")
]

urlpatterns += router.urls
