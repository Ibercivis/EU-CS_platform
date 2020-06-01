from rest_framework import viewsets
from rest_framework import permissions
from projects.api.serializers import ProjectSerializer
from projects.models import Project
from rest_framework import generics

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = []