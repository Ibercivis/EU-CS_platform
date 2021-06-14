from rest_framework import serializers
from django_countries.serializer_fields import CountryField
from django.shortcuts import get_object_or_404
from PIL import Image
from projects.models import Project, Topic, Status, Keyword, FundingBody, OriginDatabase, CustomField, ParticipationTask, GeographicExtend
from projects.forms import getCountryCode
from projects.views import saveImageWithPath
from organisations.models import Organisation

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'

class FundingBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingBody
        fields = '__all__'

class OriginDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginDatabase
        fields = '__all__'

class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = '__all__'

class ParticipationTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipationTask
        fields = '__all__'

class GeographicExtendSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographicExtend
        fields = '__all__'

class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = '__all__'


class ProjectSerializerCreateUpdate(serializers.ModelSerializer):
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True)
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())
    country = CountryField(required=False)
    start_date = serializers.DateField(format="%Y-%m-%d", required=False)
    end_date = serializers.DateField(format="%Y-%m-%d", required=False)
    fundingBody = serializers.CharField(required=False)
    originDatabase = serializers.CharField(required=False)
    keywords = serializers.CharField(required=False)
    customField = serializers.JSONField(required=False)
    mainOrganisation = serializers.PrimaryKeyRelatedField(queryset=Organisation.objects.all(), required=False)
    organisation = serializers.PrimaryKeyRelatedField(queryset=Organisation.objects.all(), many=True, required=False)

    class Meta:
        model = Project
        fields = ['id', 'name', 'aim', 'description', 'keywords', 'status', 'topic', 'start_date', 'end_date', 'url',
        'mainOrganisation', 'organisation',
         'latitude', 'longitude', 'country', 'author', 'author_email', 'image1', 'imageCredit1','image2', 'imageCredit2',
         'image3', 'imageCredit3','host', 'howToParticipate', 'doingAtHome', 'equipment', 'fundingBody', 'fundingProgram',
         'originDatabase','originURL', 'originUID', 'customField']

    def save(self, args, **kwargs):        
        fundingBody = self.validated_data.get('fundingBody')
        if(fundingBody):
            fundingBody, exist = FundingBody.objects.get_or_create(body=fundingBody)

        originDatabase =  self.validated_data.get('originDatabase')
        if(originDatabase):
            originDatabase, exist = OriginDatabase.objects.get_or_create(originDatabase=originDatabase)

        
        keywords = self.validated_data.get('keywords')
        if(keywords):
            choices = keywords.split(',')
            for choice in choices:
                if(choice != ''):
                    keyword = Keyword.objects.get_or_create(keyword=choice)
            keywords = Keyword.objects.all()
            keywords = keywords.filter(keyword__in = choices)        
        else:
            keywords = []

        
        cFields = self.validated_data.get('customField')
        if(cFields):
            paragraphs = []
            for cField in cFields:
                title = cField.get('title')
                paragraph = cField.get('paragraph')
                paragraphs.append(paragraph)
                CustomField.objects.get_or_create(title=title, paragraph=paragraph)
            cFields = CustomField.objects.all().filter(paragraph__in = paragraphs)
        else:
            cFields = []
        
        
        image1 = self.validated_data.get('image1')
        if(image1):
            photo = image1
            image = Image.open(photo)
            image_path = saveImageWithPath(image, photo.name)
            image1 = image_path

        image2 = self.validated_data.get('image2')
        if(image2):
            photo = image2
            image = Image.open(photo)
            image_path = saveImageWithPath(image, photo.name)
            image2 = image_path

        image3 = self.validated_data.get('image3')
        if(image3):
            photo = image3
            image = Image.open(photo)
            image_path = saveImageWithPath(image, photo.name)
            image3 = image_path

        country = getCountryCode(self.validated_data['latitude'],self.validated_data['longitude']).upper()

        moreItems = [('creator', args.user),('country', country), ('fundingBody', fundingBody), ('originDatabase', originDatabase),
         ('keywords', keywords), ('customField', cFields), ('image1', image1), ('image2', image2), ('image3', image3)]

        data =  dict(
            list(self.validated_data.items()) +
            list(kwargs.items()) + list(moreItems)
        )
            
        self.instance = self.create(data)

        return "success"

    def update(self, instance, validated_data, requestData):
        keywordsSent = False
        fundingBodySent = False
        originDatabaseSent = False
        mainOrganisationSent = False
        organisationSent = False
        customFieldSent = False
        image1Sent = False
        image2Sent = False
        image3Sent = False
        
        if 'keywords' in requestData:
            keywords = ""
            if requestData.get('keywords'):
                keywords = validated_data.pop('keywords')
            keywordsSent = True

        if 'fundingBody' in requestData:
            if requestData.get('fundingBody'):
                fundingBody = validated_data.pop('fundingBody')
                fundingBodySent = True
            else:
                instance.fundingBody = None
            
        if 'originDatabase' in requestData:
            if requestData.get('originDatabase'):
                originDatabase = validated_data.pop('originDatabase')
                originDatabaseSent = True
            else:
                instance.originDatabase = None

        if 'mainOrganisation' in requestData:
            if requestData.get('mainOrganisation'):
                mainOrganisation = validated_data.pop('mainOrganisation')
                mainOrganisationSent = True
            else:
                instance.mainOrganisation = None

        if 'organisation' in requestData:
            organisation = ""
            if requestData.get('organisation'):
                organisation = validated_data.pop('organisation')
            organisationSent = True

        if 'customField' in requestData:
            cFields = ""
            if requestData.get('customField'):
                cFields = validated_data.pop('customField')
            customFieldSent = True

        if 'image1' in requestData:
            if requestData.get('image1'):
                image1 = validated_data.pop('image1')
            image1Sent = True

        if 'image2' in requestData:
            if requestData.get('image2'):
                image2 = validated_data.pop('image2')
            image2Sent = True

        if 'image3' in requestData:
            if requestData.get('image3'):
                image3 = validated_data.pop('image3')
            image3Sent = True

        super().update(instance, validated_data)

        if(keywordsSent):
            choices = keywords.split(',')
            for choice in choices:
                if(choice != ''):
                    keyword = Keyword.objects.get_or_create(keyword=choice)
            keywords = Keyword.objects.all()
            keywords = keywords.filter(keyword__in= choices)
            instance.keywords.set(keywords)

        if(fundingBodySent):
            fundingBody, exist = FundingBody.objects.get_or_create(body=fundingBody)
            instance.fundingBody = fundingBody

        if(originDatabaseSent):
            originDatabase, exist = OriginDatabase.objects.get_or_create(originDatabase=originDatabase)
            instance.originDatabase = originDatabase
        
        if(mainOrganisationSent):
            instance.mainOrganisation = mainOrganisation

        if(organisationSent):
            instance.organisation.set(organisation)

        #CustomField
        if(customFieldSent):
            if(cFields):
                paragraphs = []
                for cField in cFields:
                    title = cField.get('title')
                    paragraph = cField.get('paragraph')
                    paragraphs.append(paragraph)
                    CustomField.objects.get_or_create(title=title, paragraph=paragraph)
                cFields = CustomField.objects.all().filter(paragraph__in = paragraphs)
            else:
                cFields = []
            instance.customField.set(cFields)
        
        if(image1Sent):
            if(image1):
                photo = image1
                image = Image.open(photo)
                image_path = saveImageWithPath(image, photo.name)
                instance.image1 = image_path

        if(image2Sent):
            if(image2):
                photo = image2
                image = Image.open(photo)
                image_path = saveImageWithPath(image, photo.name)
                instance.image2 = image_path

        if(image3Sent):
            if(image3):
                photo = image3
                image = Image.open(photo)
                image_path = saveImageWithPath(image, photo.name)
                instance.image3 = image_path

        if 'latitude' in requestData and 'longitude' in requestData:
            instance.country = getCountryCode(self.validated_data['latitude'],self.validated_data['longitude']).upper()

        instance.save()
        return instance
   

class ProjectSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(many=True, required=False)
    status = StatusSerializer(many=False)
    keywords = KeywordSerializer(many=True, required=False)
    fundingBody = FundingBodySerializer(many=False, required=False)
    originDatabase = OriginDatabaseSerializer(many=False, required=False)
    customField = CustomFieldSerializer(many=True, required=False)
    country = CountryField(required=False)
    start_date = serializers.DateTimeField(format="%Y-%m-%d", required=False)
    end_date = serializers.DateTimeField(format="%Y-%m-%d", required=False)
    mainOrganisation = OrganisationSerializer(many=False, required=False)
    organisation = OrganisationSerializer(many=True, required=False)

    class Meta:
        model = Project
        fields = ['id', 'name', 'aim', 'description', 'keywords', 'status', 'topic', 'start_date', 'end_date', 'url',
         'mainOrganisation', 'organisation',
         'latitude', 'longitude', 'country', 'image1', 'imageCredit1','image2', 'imageCredit2',
         'image3', 'imageCredit3','host', 'howToParticipate', 'doingAtHome', 'equipment', 'fundingBody', 'fundingProgram',
         'originDatabase','originURL', 'originUID', 'featured', 'customField', 'dateCreated', 'origin']
