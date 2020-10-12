from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects/topic', views.TopicViewSet, basename='topic')
router.register(r'projects/status', views.StatusViewSet, basename='status')
router.register(r'projects/participation_task', views.ParticipationTaskViewSet, basename='participation_task')
router.register(r'projects/geographic_extend', views.GeographicExtendViewSet, basename='geographic_extend')

urlpatterns = [
    path('projects/', views.ProjectList.as_view(), name="api_projects"),
    path('projects/<int:pk>', views.ProjectDetail.as_view(), name="api_project_detail"),
    path('projects/<int:pk>/approved', views.approved_project, name="approve_project"),
    path('projects/<int:pk>/hidden', views.hidden_project, name="hide_project"),
    path('projects/<int:pk>/featured', views.set_featured_project, name="set_featured_project"),
    path('projects/<int:pk>/followed', views.follow_project, name="follow_project"),
]

urlpatterns += router.urls