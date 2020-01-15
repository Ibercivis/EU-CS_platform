from django import forms
from django.db import models
from django.utils import timezone
from .models import Document
from datetime import datetime, date
from django.forms import ModelForm


class DocumentForm(forms.ModelForm):
    '''
        document_name = forms.CharField(max_length=100)
        author = forms.CharField(max_length=100)
        description = forms.CharField(max_length=100)
        url = forms.CharField(max_length=200)
        document = forms.FileField()
    '''
    class Meta:
        model = Document
        fields = ["name", "author", "description", "url"]
        

    def save(self, args):
        publication_date = datetime.now()
        '''
        print(self.data['document'])
        doc = Document(name = self.data['name'], url = self.data['url'], 
                         author = self.data['author'], description = self.data['description'], 
                         datePublished = publication_date, document='1')
        doc.save()
        '''
        doc = super(DocumentForm, self).save(commit=False)
        doc.datePublished = publication_date
        doc.save()
        return 'success'