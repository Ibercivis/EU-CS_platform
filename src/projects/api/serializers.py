from rest_framework import serializers
from django_countries.serializer_fields import CountryField
from django.shortcuts import get_object_or_404
from projects.models import Project, Topic, Status, Keyword, FundingBody, OriginDatabase, CustomField
from projects.forms import getCountryCode

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


class ProjectSerializerCreate(serializers.ModelSerializer):
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True)
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())
    country = CountryField(required=False)
    start_date = serializers.DateField(format="%Y-%m-%d", required=False)
    end_date = serializers.DateField(format="%Y-%m-%d", required=False)
    fundingBody = serializers.CharField(required=False)
    originDatabase = serializers.CharField(required=False)
    keywords = serializers.CharField(required=False)

    class Meta:
        model = Project
        fields = ['id', 'name', 'aim', 'description', 'keywords', 'status', 'topic', 'start_date', 'end_date', 'url',
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

        '''
        cFields = self.validated_data.get('customField')
        if(cFields):
            paragraphs = []
            for cField in cFields:
                paragraphs.append(cField.paragraph)
                CustomField.objects.get_or_create(title=cField.title, paragraph=cField.paragraph)
            cfields = CustomField.objects.all().filter(paragraph__in = paragraphs)
            project = get_object_or_404(Project, id=pk)
            project.customField.set(cfields)
        '''
        
        country = getCountryCode(self.validated_data['latitude'],self.validated_data['longitude']).upper()

        moreItems = [('creator', args.user),('country', country), ('fundingBody', fundingBody), ('originDatabase', originDatabase),
         ('keywords', keywords),]

        data =  dict(
            list(self.validated_data.items()) +
            list(kwargs.items()) + list(moreItems)
        )
            
        self.instance = self.create(data)

        return "success"

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

    class Meta:
        model = Project
        fields = ['id', 'name', 'aim', 'description', 'keywords', 'status', 'topic', 'start_date', 'end_date', 'url',
         'latitude', 'longitude', 'country', 'author', 'author_email', 'image1', 'imageCredit1','image2', 'imageCredit2',
         'image3', 'imageCredit3','host', 'howToParticipate', 'doingAtHome', 'equipment', 'fundingBody', 'fundingProgram',
         'originDatabase','originURL', 'originUID', 'featured', 'customField', 'dateCreated', 'origin']