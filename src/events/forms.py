from django import forms
from django.db import models
from .models import Event

class EventForm(forms.Form):
    title = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'placeholder':'Title of the event'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'A little description of the event. Max 1000 characters'}), max_length = 1000)
    place = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'placeholder':'Place where event happens'}))
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    url = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder':'Please provide a URL to an external web site for the event'}),required=False)
    
    def save(self, args):
        event = Event(title =  self.data['title'], description =  self.data['description'], place =  self.data['place'],
                    start_date =  self.data['start_date'], end_date =  self.data['end_date'], url =  self.data['url']
                )
        event.save()
