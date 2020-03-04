from django import forms
from django.db import models
from django.utils import timezone
from .models import Resource, Keyword, Category, Audience, Theme
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from django.forms import ModelForm
from django_select2.forms import Select2MultipleWidget
from authors.models import Author

class ResourceForm(forms.ModelForm):
    abstract = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), max_length=1000)   
    choices = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    choicesSelected = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    keywords = forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(parent__isnull=True))
    categorySelected = forms.CharField(widget=forms.HiddenInput(),required=False)
    authorsCollection = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    selectedAuthors = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    authors = forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False)
    audience = forms.ModelChoiceField(queryset=Audience.objects.all())
    theme = forms.ModelMultipleChoiceField(queryset=Theme.objects.all(), widget=Select2MultipleWidget, required=False)
    imageURL = forms.CharField(max_length=300)
    resource_DOI = forms.CharField(max_length=100)
    year_of_publication = forms.IntegerField()

    class Meta:
        model = Resource
        fields = ["name", "abstract", "url", "audience", "theme",
         "keywords", "license", "publisher", "category", "authors","author_email",
         "imageURL", "resource_DOI", "year_of_publication"]
        
        

    def save(self, args):
        publication_date = datetime.now()
        rsc = super(ResourceForm, self).save(commit=False)
        category = get_object_or_404(Category, id=self.data['categorySelected'])

        pk = self.data.get('resourceID', '')
        if pk:
            rsc = get_object_or_404(Resource, id=pk)
            rsc.name = self.data['name']
            rsc.abstract = self.data['abstract']
            rsc.url = self.data['url']
            rsc.license = self.data['license']
            rsc.audience = get_object_or_404(Audience, id=self.data['audience'])
            rsc.publisher = self.data['publisher']
        else:
            rsc.dateUploaded = publication_date
            rsc.creator = args.user

        rsc.inLanguage = self.data['language']        
        rsc.author_email = self.data['author_email']
        rsc.imageURL = self.data['imageURL']
        rsc.resourceDOI = self.data['resource_DOI']
        rsc.datePublished = self.data['year_of_publication']
        rsc.category = category
        rsc.save()

        rsc.theme.set(self.data.getlist('theme'))

        # Keywords
        choices = self.data['choices']
        choices = choices.split(',')
        for choice in choices:
            if(choice != ''):
                keyword = Keyword.objects.get_or_create(keyword=choice)                   
        keywords = Keyword.objects.all()
        keywords = keywords.filter(keyword__in = choices)
        rsc.keywords.set(keywords)

        # Authors
        authors = self.data['authorsCollection']
        authors = authors.split(',')
        for author in authors:
            if(author != ''):
                Author.objects.get_or_create(author=author)
        authorsCollection = Author.objects.all()
        authors = authorsCollection.filter(author__in = authors)
        rsc.authors.set(authors)

        return 'success'