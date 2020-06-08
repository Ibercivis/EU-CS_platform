from django.http import Http404
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND)
from rest_framework.views import APIView
from projects.api.serializers import ProjectSerializer, ProjectSerializerCreateUpdate
from projects.models import Project
from projects.views import getCooperators


class ProjectList(APIView):
    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = ProjectSerializerCreateUpdate(data=request.data)
        if serializer.is_valid():
            serializer.save(request)
            serializerReturn = ProjectSerializer(Project.objects.get(pk=serializer.data.get('id')), context={'request': request})
            return Response(serializerReturn.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class PermissionClass(BasePermission):   
    def has_permission(self, request, view):
        METHODS_WITH_PERMISSION = ["DELETE", "PUT", "POST"]
        if request.method in  METHODS_WITH_PERMISSION:
            return request.user and request.user.is_active
        return True

class ProjectDetail(APIView):
    permission_classes = (PermissionClass,)
    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = ProjectSerializer(project, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        project = self.get_object(pk)
        if request.user == project.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            serializer = ProjectSerializerCreateUpdate(project, data=request.data)
            if serializer.is_valid():
                serializer.update(project, serializer.validated_data, request.data)
                serializerReturn = ProjectSerializer(Project.objects.get(pk=serializer.data.get('id')), context={'request': request})
                return Response(serializerReturn.data)
        else:
            return Response({"This user can't update this project"}, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project = self.get_object(pk)
        if request.user == project.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            project.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            return Response({"This user can't delete this project"}, status=HTTP_400_BAD_REQUEST)