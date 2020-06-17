from rest_framework import serializers
from django.shortcuts import get_object_or_404
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

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    audience = AudienceSerializer(many=True)
    theme = ThemeSerializer(many=True)
    keywords = KeywordSerializer(many=True, required=False)

    class Meta:
        model = Resource
        fields = ['id', 'name', 'url', 'abstract' ,'image', 'image1', 'image2','authors', 'author_email', 'audience', 'dateUploaded', 'keywords',
            'category', 'license', 'publisher', 'datePublished', 'theme', 'inLanguage', 'resourceDOI', 'featured']
