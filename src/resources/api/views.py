from django.contrib.contenttypes.models import ContentType
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
from resources.api.serializers import ResourceSerializer, AudienceSerializer, ThemeSerializer, CategorySerializer, ResourceSerializerCreateUpdate,EducationLevelSerializer, LearningResourceTypeSerializer, TrainingResourceSerializer, TrainingResourceSerializerCreateUpdate
from resources.models import Resource, ApprovedResources, Audience, Theme, Category, EducationLevel, LearningResourceType
from resources.views import getCooperators, setResourceHidden, bookmarkResource
from reviews.models import Review

class AdminPermissionsClass(BasePermission):
    def has_permission(self, request, view):
        METHODS_WITH_PERMISSION = ["DELETE", "PUT", "POST"]
        if request.method in  METHODS_WITH_PERMISSION:
            return request.user.is_staff
        return True

class AudienceViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminPermissionsClass,)
    serializer_class = AudienceSerializer
    queryset = Audience.objects.all()

class ThemeViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminPermissionsClass,)
    serializer_class = ThemeSerializer
    queryset = Theme.objects.all()

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminPermissionsClass,)
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class EducationLevelViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminPermissionsClass,)
    serializer_class = EducationLevelSerializer
    queryset = EducationLevel.objects.all()

class LearningResourceTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminPermissionsClass,)
    serializer_class = LearningResourceTypeSerializer
    queryset = LearningResourceType.objects.all()

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
        resources = Resource.objects.all().filter(~Q(isTrainingResource=True))
        resources = self.applyFilters(request, resources)
        serializer = ResourceSerializer(resources, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ResourceSerializerCreateUpdate(data=request.data)
        if serializer.is_valid():
            serializer.save(request)
            serializerReturn = ResourceSerializer(Resource.objects.get(pk=serializer.data.get('id')), context={'request': request})
            return Response(serializerReturn.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class PermissionClass(BasePermission):   
    def has_permission(self, request, view):
        METHODS_WITH_PERMISSION = ["DELETE", "PUT", "POST"]
        if request.method in  METHODS_WITH_PERMISSION:
            return request.user and request.user.is_active
        return True


class ResourceDetail(APIView):
    permission_classes = (PermissionClass,)
    def get_object(self, pk):
        try:
            return Resource.objects.get(pk=pk)
        except Resource.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        resource = self.get_object(pk)
        serializer = ResourceSerializer(resource, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        resource = self.get_object(pk)
        if request.user == resource.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            serializer = ResourceSerializerCreateUpdate(resource, data=request.data)
            if serializer.is_valid():
                serializer.update(resource, serializer.validated_data, request.data)
                serializerReturn = ResourceSerializer(Resource.objects.get(pk=serializer.data.get('id')), context={'request': request})
                return Response(serializerReturn.data)
        else:
            return Response({"This user can't update this resource"}, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        resource = self.get_object(pk)
        if request.user == resource.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            serializer = ResourceSerializerCreateUpdate(resource, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.update(resource, serializer.validated_data, request.data)
                serializerReturn = ResourceSerializer(Resource.objects.get(pk=serializer.data.get('id')), context={'request': request})
                return Response(serializerReturn.data)
        else:
            return Response({"This user can't update this resource"}, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        resource = self.get_object(pk)
        if request.user == resource.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            resource.delete()
            reviews = Review.objects.filter(content_type=ContentType.objects.get(model="resource"), object_pk=pk)
            for r in reviews:
                r.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            return Response({"This user can't delete this resource"}, status=HTTP_400_BAD_REQUEST)


class TrainingResourceList(APIView):

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
        resources = Resource.objects.all().filter(isTrainingResource=True)
        resources = self.applyFilters(request, resources)
        serializer = TrainingResourceSerializer(resources, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = TrainingResourceSerializerCreateUpdate(data=request.data)
        if serializer.is_valid():
            serializer.save(request)
            serializerReturn = TrainingResourceSerializer(Resource.objects.get(pk=serializer.data.get('id')), context={'request': request})
            return Response(serializerReturn.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class TrainingResourceDetail(APIView):
    permission_classes = (PermissionClass,)
    def get_object(self, pk):
        try:
            return Resource.objects.get(pk=pk)
        except Resource.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        resource = self.get_object(pk)
        serializer = TrainingResourceSerializer(resource, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        resource = self.get_object(pk)
        if request.user == resource.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            serializer = TrainingResourceSerializerCreateUpdate(resource, data=request.data)
            if serializer.is_valid():
                serializer.update(resource, serializer.validated_data, request.data)
                serializerReturn = TrainingResourceSerializer(Resource.objects.get(pk=serializer.data.get('id')), context={'request': request})
                return Response(serializerReturn.data)
        else:
            return Response({"This user can't update this resource"}, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        resource = self.get_object(pk)
        if request.user == resource.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            serializer = TrainingResourceSerializerCreateUpdate(resource, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.update(resource, serializer.validated_data, request.data)
                serializerReturn = TrainingResourceSerializer(Resource.objects.get(pk=serializer.data.get('id')), context={'request': request})
                return Response(serializerReturn.data)
        else:
            return Response({"This user can't update this resource"}, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        resource = self.get_object(pk)
        if request.user == resource.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            resource.delete()
            reviews = Review.objects.filter(content_type=ContentType.objects.get(model="resource"), object_pk=pk)
            for r in reviews:
                r.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            return Response({"This user can't delete this resource"}, status=HTTP_400_BAD_REQUEST)


# @api_view(['PUT'])
# @permission_classes([AdminPermissionsClass])
# def approved_resource(request, pk):
#    approved = request.data.get('value')
#    setResourceApproved(pk, approved)
#    return Response(status=HTTP_204_NO_CONTENT)

@api_view(['PUT'])
@permission_classes([AdminPermissionsClass])
def hidden_resource(request, pk):
    hidden = request.data.get('value')
    setResourceHidden(pk, hidden)
    return Response(status=HTTP_204_NO_CONTENT)


# @api_view(['PUT'])
# @permission_classes([AdminPermissionsClass])
# def set_featured_resource(request, pk):
#    featured = request.data.get('value')
#    setResourceFeatured(pk, featured)
#    return Response(status=HTTP_204_NO_CONTENT)

# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def save_resource(request, pk):
#    userId = request.user.id
#    save = request.data.get('value')
#    Resource(pk, userId, save)
#    return Response(status=HTTP_204_NO_CONTENT)
