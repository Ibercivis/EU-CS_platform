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
from resources.models import Resource, ApprovedResources

class ResourceList(APIView):

    def applyFilters(self, request, resources):
        approvedResources = ApprovedResources.objects.all().values_list('resource_id',flat=True)

        keywords = request.query_params.get('keywords', None)
        if keywords is not None:
            resources = resources.filter( Q(name__icontains = keywords) |
                                    Q(keywords__keyword__icontains = keywords) ).distinct()

        language = request.query_params.get('language', None)
        if language is not None:
            resources = resources.filter(inLanguage = language)

        license = request.query_params.get('license', None)
        if license is not None:
            resources = resources.filter(license__icontains=license)

        theme = request.query_params.get('theme', None)
        if theme is not None:
            resources = resources.filter(theme=theme)

        category = request.query_params.get('category', None)
        if category is not None:
            resources = resources.filter(category=category)

        if request.GET.get('approvedCheck'):
            if request.GET['approvedCheck'] == 'On':
                resources = resources.filter(id__in=approvedResources)
            if request.GET['approvedCheck'] == 'Off':
                resources = resources.exclude(id__in=approvedResources)
            if request.GET['approvedCheck'] == 'All':
                resources = resources
        else:
            resources = resources.filter(id__in=approvedResources)

        return resources

    def get(self, request, format=None):
        resources = Resource.objects.all()
        resources = self.applyFilters(request, resources)
        serializer = ResourceSerializer(resources, many=True, context={'request': request})
        return Response(serializer.data)