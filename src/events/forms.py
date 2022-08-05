from django import forms
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .models import Event


class EventForm(forms.Form):
    title = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            help_text=_('Please write the title of the event.'),
            label=_('Title'))
    description = forms.CharField(widget=forms.Textarea(), max_length = 3000,
            help_text=_('Please add a brief description of the event.'),
            label=_('Description'))
    place = forms.CharField(max_length=200,widget=forms.TextInput(),required=False,
            help_text=_('Please indicate the location of the event.'),
            label=_('Place'))
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}),
            label=_('Start date'))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}),
            help_text=_('Please indicate the start and end dates of the event.'),
            label=_('End date'))
    hour = forms.TimeField(widget=forms.TextInput(attrs={'type': 'time'}), required=False,
            help_text=_('Please indicate the start time of the event.'),
            label=_('Hour'))   
    url = forms.CharField(max_length=200, label=_('URL'),widget=forms.TextInput(),required=False,
            help_text=_('Please provide a URL to an external web site for the event.'))
    
    def save(self, args):
        pk = self.data.get('eventID', '')
        hour = self.data['hour']
        if hour == '':
            hour = None
        if pk:
            event = get_object_or_404(Event, id=pk)
            event.title = self.data['title']
            event.description = self.data['description']            
            event.place = self.data['place']
            event.start_date = self.data['start_date']
            event.end_date = self.data['end_date']
            event.hour = hour
            event.url = self.data['url']
            event.creator=args.user
        else:
            event = Event(title =  self.data['title'], description =  self.data['description'], place =  self.data['place'],
                        start_date =  self.data['start_date'], end_date =  self.data['end_date'], hour = hour, url =  self.data['url'],
                        creator = args.user
                    )
        event.save()
