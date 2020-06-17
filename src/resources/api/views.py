from django.db.models import Q
from django.http import Http404
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND)
from rest_framework.views import APIView
from resources.api.serializers import ResourceSerializer
from resources.models import Resource

class ResourceList(APIView):

    def get(self, request, format=None):
        resources = Resource.objects.all()

        #resources = self.applyFilters(request, resources)

        serializer = ResourceSerializer(resources, many=True, context={'request': request})
        return Response(serializer.data)