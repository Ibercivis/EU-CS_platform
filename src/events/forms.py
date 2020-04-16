from django import forms
from django.shortcuts import get_object_or_404
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
        pk = self.data.get('eventID', '')
        if pk:
            event = get_object_or_404(Event, id=pk)
            event.title = self.data['title']
            event.description = self.data['description']            
            event.place = self.data['place']
            event.start_date = self.data['start_date']
            event.end_date = self.data['end_date']
            event.url = self.data['url']
        else:
            event = Event(title =  self.data['title'], description =  self.data['description'], place =  self.data['place'],
                        start_date =  self.data['start_date'], end_date =  self.data['end_date'], url =  self.data['url']
                    )
        event.save()
