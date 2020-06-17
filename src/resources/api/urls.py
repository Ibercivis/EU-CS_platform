from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'resources/audience', views.AudienceViewSet, basename='audience')
router.register(r'resources/theme', views.ThemeViewSet, basename='theme')
router.register(r'resources/category', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('resources/', views.ResourceList.as_view(), name="api_resources"),
]

urlpatterns += router.urls