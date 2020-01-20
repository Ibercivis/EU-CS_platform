from django import forms
from django.db import models
from django.utils import timezone
from .models import Document
from datetime import datetime, date
from django.forms import ModelForm


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ["name", "author", "about", "abstract", "url", "audience",
         "inLanguage", "keywords", "license", "publisher"]
        

    def save(self, args):
        publication_date = datetime.now()        
        doc = super(DocumentForm, self).save(commit=False)
        doc.datePublished = publication_date
        doc.save()
        return 'success'