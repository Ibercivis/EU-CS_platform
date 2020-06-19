from datetime import datetime
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from authors.models import Author
from resources.models import Resource, Keyword, Theme, Audience, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AudienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audience
        fields = '__all__'

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    audience = AudienceSerializer(many=True)
    theme = ThemeSerializer(many=True)
    authors = AuthorSerializer(many=True)
    keywords = KeywordSerializer(many=True, required=False)

    class Meta:
        model = Resource
        fields = ['id', 'name', 'url', 'abstract' , 'image1', 'image2','authors', 'author_email', 'audience', 'dateUploaded', 'keywords',
            'category', 'license', 'publisher', 'datePublished', 'theme', 'inLanguage', 'resourceDOI', 'featured']


class ResourceSerializerCreateUpdate(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=False)
    audience = serializers.PrimaryKeyRelatedField(queryset=Audience.objects.all(), many=True)
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), many=True)
    keywords = serializers.CharField(required=False)
    authors = serializers.CharField(required=True)

    class Meta:
        model = Resource
        fields = ['id', 'name', 'url', 'abstract' , 'image1', 'image2','authors', 'author_email', 'audience', 'keywords',
            'category', 'license', 'publisher', 'datePublished', 'theme', 'inLanguage', 'resourceDOI', 'featured']

    def validate(self, data):
        if data['theme'] == []:
            raise serializers.ValidationError({'theme': ["This field is required."]})
        if data['audience'] == []:
            raise serializers.ValidationError({'audience': ["This field is required."]})

        return data

    def save(self, args, **kwargs):               
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
        
        # Authors
        authors = self.validated_data.get('authors')
        if(authors):
            choices = authors.split(',')
            for choice in choices:
                if(choice != ''):
                    Author.objects.get_or_create(author=choice)
            authors = Author.objects.all()
            authors = authors.filter(author__in = choices)
        else:
            authors = []

        publication_date = datetime.now()

        moreItems = [('creator', args.user),('keywords', keywords), ('authors', authors), ('dateUploaded', publication_date)]

        data =  dict(
            list(self.validated_data.items()) +
            list(kwargs.items()) + list(moreItems)
        )
            
        self.instance = self.create(data)

        return "success"

    def update(self, instance, validated_data, requestData):
        keywordsSent = False
        authorsSent = False
        if 'keywords' in requestData:
            keywords = ""
            if requestData.get('keywords'):
                keywords = validated_data.pop('keywords')
            keywordsSent = True

        if 'authors' in requestData:
            if requestData.get('authors'):
                authors = validated_data.pop('authors')
                authorsSent = True
            else:
                instance.authors  = None                           

        super().update(instance, validated_data)

        if(keywordsSent):
            choices = keywords.split(',')
            for choice in choices:
                if(choice != ''):
                    keyword = Keyword.objects.get_or_create(keyword=choice)
            keywords = Keyword.objects.all()
            keywords = keywords.filter(keyword__in = choices)
            instance.keywords.set(keywords)

        if(authorsSent):
            for choice in choices:
                if(choice != ''):
                    author, exist = Author.objects.get_or_create(author=choice)
            authors = Author.objects.all()
            authors = authors.filter(author__in = choices)
            instance.authors.set(authors)

        instance.save()
        return instance
