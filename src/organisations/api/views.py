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
from organisations.api.serializers import OrganisationTypeSerializer, OrganisationSerializer, OrganisationSerializerCreateUpdate
from organisations.models import OrganisationType, Organisation
from organisations.views import getCooperators

class AdminPermissionsClass(BasePermission):
    def has_permission(self, request, view):
        METHODS_WITH_PERMISSION = ["DELETE", "PUT", "POST"]
        if request.method in  METHODS_WITH_PERMISSION:
            return request.user.is_staff
        return True

class PermissionClass(BasePermission):   
    def has_permission(self, request, view):
        METHODS_WITH_PERMISSION = ["DELETE", "PUT", "POST"]
        if request.method in  METHODS_WITH_PERMISSION:
            return request.user and request.user.is_active
        return True

class OrganisationTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminPermissionsClass,)
    serializer_class = OrganisationTypeSerializer
    queryset = OrganisationType.objects.all()

class OrganisationList(APIView):

    def applyFilters(self, request, organisations):
        country = request.query_params.get('country', None)
        if country is not None:
            organisations = organisations.filter(country = country)

        orgType = request.query_params.get('orgType', None)
        if orgType is not None:
            organisations = organisations.filter(orgType=orgType)

        return organisations

    def get(self, request, format=None):
        organisations = Organisation.objects.all()
        organisations = self.applyFilters(request, organisations)
        serializer = OrganisationSerializer(organisations, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = OrganisationSerializerCreateUpdate(data=request.data)
        if serializer.is_valid():
            serializer.save(request)
            serializerReturn = OrganisationSerializer(Organisation.objects.get(pk=serializer.data.get('id')), context={'request': request})
            return Response(serializerReturn.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class OrganisationDetail(APIView):
    permission_classes = (PermissionClass,)
    def get_object(self, pk):
        try:
            return Organisation.objects.get(pk=pk)
        except Organisation.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        organisation = self.get_object(pk)
        serializer = OrganisationSerializer(organisation, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        organisation = self.get_object(pk)
        if request.user == organisation.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            serializer = OrganisationSerializerCreateUpdate(organisation, data=request.data)
            if serializer.is_valid():
                serializer.update(organisation, serializer.validated_data, request.data)
                serializerReturn = OrganisationSerializer(Organisation.objects.get(pk=serializer.data.get('id')), context={'request': request})
                return Response(serializerReturn.data)
        else:
            return Response({"This user can't update this organisation"}, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        organisation = self.get_object(pk)
        if request.user == organisation.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            serializer = OrganisationSerializerCreateUpdate(organisation, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.update(organisation, serializer.validated_data, request.data)
                serializerReturn = OrganisationSerializer(Organisation.objects.get(pk=serializer.data.get('id')), context={'request': request})
                return Response(serializerReturn.data)
        else:
            return Response({"This user can't update this organisation"}, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        organisation = self.get_object(pk)
        if request.user == organisation.creator or request.user.is_staff or request.user.id in getCooperators(pk):
            organisation.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            return Response({"This user can't delete this organisation"}, status=HTTP_400_BAD_REQUEST)