from django import forms
from django.db import models
from django.utils import timezone
from .models import Document
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from django.forms import ModelForm

class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ["name", "about", "abstract", "url", "audience",
         "keywords", "license", "publisher"]
        

    def save(self, args):
        publication_date = datetime.now()        
        doc = super(DocumentForm, self).save(commit=False)
        
        pk = self.data.get('documentID', '')
        if pk:
            doc = get_object_or_404(Document, id=pk)
            doc.name = self.data['name']
            doc.about = self.data['about']
            doc.abstract = self.data['abstract']
            doc.url = self.data['url']
            doc.license = self.data['license']
            doc.audience = self.data['audience']
            doc.publisher = self.data['publisher']
            doc.keywords = self.data['keywords']
        else:
            doc.datePublished = publication_date
            doc.author = args.user

        doc.inLanguage = self.data['language']     

        doc.save()
        return 'success'