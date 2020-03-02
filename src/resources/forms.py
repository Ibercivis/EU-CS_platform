from django import forms
from django.db import models
from django.utils import timezone
from .models import Resource, Keyword, Category
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from django.forms import ModelForm
from django_select2.forms import Select2MultipleWidget

class ResourceForm(forms.ModelForm):
    abstract = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), max_length=300)   
    choices = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    choicesSelected = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    keywords = forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(parent__isnull=True))
    categorySelected = forms.CharField(widget=forms.HiddenInput(),required=False)

    class Meta:
        model = Resource
        fields = ["name", "about", "abstract", "url", "audience",
         "keywords", "license", "publisher", "category"]
        
        

    def save(self, args):
        publication_date = datetime.now()        
        rsc = super(ResourceForm, self).save(commit=False)
        category = get_object_or_404(Category, id=self.data['categorySelected'])

        pk = self.data.get('resourceID', '')
        if pk:
            rsc = get_object_or_404(Resource, id=pk)
            rsc.name = self.data['name']
            rsc.about = self.data['about']
            rsc.abstract = self.data['abstract']
            rsc.url = self.data['url']
            rsc.license = self.data['license']
            rsc.audience = self.data['audience']
            rsc.publisher = self.data['publisher']            
        else:
            rsc.datePublished = publication_date
            rsc.author = args.user

        rsc.inLanguage = self.data['language']     
        rsc.category = category
        rsc.save()

        choices = self.data['choices']
        choices = choices.split(',')
        for choice in choices:
            if(choice != ''):
                keyword = Keyword.objects.get_or_create(keyword=choice)                   
        keywords = Keyword.objects.all()
        keywords = keywords.filter(keyword__in = choices)
        rsc.keywords.set(keywords)

        return 'success'