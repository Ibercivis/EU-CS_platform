from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK)
from projects.api.serializers import ProjectSerializer
from projects.models import Project



@api_view(['GET', ])
#@permission_classes((IsAuthenticated, ))
def api_projects(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True, context={'request': request})
    return Response(serializer.data)
    
@api_view(['GET', ])
def api_project_detail(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({'error': 'Project with this key not exist'},status=HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectSerializer(project, context={'request': request})
        return Response(serializer.data)