from datetime import datetime
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django_countries.serializer_fields import CountryField
from PIL import Image
from organisations.models import Organisation, OrganisationType
from projects.forms import getCountryCode
from organisations.views import saveImageWithPath

class OrganisationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationType
        fields = '__all__'


class OrganisationSerializer(serializers.ModelSerializer):
    orgType = OrganisationTypeSerializer(many=False)
    country = CountryField(required=False)
    class Meta:
        model = Organisation
        fields = ['id', 'name', 'url', 'description' , 'orgType', 'logo','contactPoint', 'contactPointEmail', 'latitude', 'longitude','country']


class OrganisationSerializerCreateUpdate(serializers.ModelSerializer):
    orgType = serializers.PrimaryKeyRelatedField(queryset=OrganisationType.objects.all(), many=False)
    country = CountryField(required=False)

    class Meta:
        model = Organisation
        fields = ['id', 'name', 'url', 'description' , 'orgType', 'logo','contactPoint', 'contactPointEmail', 'latitude', 'longitude','country']

    def save(self, args, **kwargs):               

        logo = self.validated_data.get('logo')
        if(logo):
            photo = logo
            image = Image.open(photo)
            image_path = saveImageWithPath(image, photo.name)
            logo = image_path

        moreItems = [('creator', args.user), ('logo', logo)]

        data =  dict(
            list(self.validated_data.items()) +
            list(kwargs.items()) + list(moreItems)
        )
            
        self.instance = self.create(data)

        return "success"