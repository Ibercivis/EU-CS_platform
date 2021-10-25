from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'resources/audience', views.AudienceViewSet, basename='audience')
router.register(r'resources/theme', views.ThemeViewSet, basename='theme')
router.register(r'resources/category', views.CategoryViewSet, basename='category')
router.register(r'training_resources/education_level', views.EducationLevelViewSet, basename='educationLevel')
router.register(r'training_resources/learning_resource_level', views.LearningResourceTypeViewSet, basename='learningResourceType')

urlpatterns = [
    path('resources/', views.ResourceList.as_view(), name="api_resources"),
    path('resources/<int:pk>', views.ResourceDetail.as_view(), name="api_resource_detail"),
    # path('resources/<int:pk>/approved', views.approved_resource, name="approve_resource"),
    path('resources/<int:pk>/hidden', views.hidden_resource, name="hide_resource"),
    # path('resources/<int:pk>/featured', views.set_featured_resource, name="set_featured_resource"),
    # path('resources/<int:pk>/saved', views.save_resource, name="save_resource"),
    path('training_resources/', views.TrainingResourceList.as_view(), name="api_training_resources"),
    path('training_resources/<int:pk>', views.TrainingResourceDetail.as_view(), name="api_training_resource_detail"),
    # path('training_resources/<int:pk>/approved', views.approved_resource, name="approve_resource"),
    path('training_resources/<int:pk>/hidden', views.hidden_resource, name="hide_resource"),
    # path('training_resources/<int:pk>/featured', views.set_featured_resource, name="set_featured_resource"),
    # path('training_resources/<int:pk>/saved', views.save_resource, name="save_resource"),
]

urlpatterns += router.urls
