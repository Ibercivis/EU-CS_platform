from django import forms
from django.db import models
from django.utils import timezone
from .models import Resource
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from django.forms import ModelForm

class ResourceForm(forms.ModelForm):
    abstract = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), max_length=300)
    class Meta:
        model = Resource
        fields = ["name", "about", "abstract", "url", "audience",
         "keywords", "license", "publisher"]
        
        

    def save(self, args):
        publication_date = datetime.now()        
        rsc = super(ResourceForm, self).save(commit=False)
        
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
            rsc.keywords = self.data['keywords']
        else:
            rsc.datePublished = publication_date
            rsc.author = args.user

        rsc.inLanguage = self.data['language']     

        rsc.save()
        return 'success'