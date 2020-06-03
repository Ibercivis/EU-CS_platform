from rest_framework import serializers
from django_countries.serializer_fields import CountryField
from projects.models import Project, Topic, Status, Keyword, FundingBody, OriginDatabase, CustomField

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


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    topic = TopicSerializer(many=True, required=False)
    status = StatusSerializer(many=False, required=False)
    keywords = KeywordSerializer(many=True, required=False)
    fundingBody = FundingBodySerializer(many=False, required=False)
    originDatabase = OriginDatabaseSerializer(many=False, required=False)
    customField = CustomFieldSerializer(many=True, required=False)
    country = CountryField()
    class Meta:
        model = Project
        fields = ['id', 'name', 'aim', 'description', 'keywords', 'status', 'topic', 'start_date', 'end_date', 'url',
         'latitude', 'longitude', 'country', 'author', 'author_email', 'image1', 'imageCredit1','image2', 'imageCredit2',
         'image3', 'imageCredit3','host', 'howToParticipate', 'doingAtHome', 'equipment', 'fundingBody', 'fundingProgram',
         'originDatabase','originURL', 'originUID', 'featured', 'customField', 'dateCreated', 'origin'] 
