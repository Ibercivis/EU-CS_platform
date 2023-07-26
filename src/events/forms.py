from django import forms
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .models import Event
from organisations.models import Organisation
from projects.models import Project
from django_select2 import forms as s2forms
import pytz


EVENT_TYPE_CHOICES = [
    ('online', 'On-line event'),
    ('face-to-face', 'Face-to-face event'),
]


class EventForm(forms.Form):
    title = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            help_text=_('Please write the title of the event.'),
            label=_('Title'))
    description = forms.CharField(widget=forms.Textarea(), max_length = 3000,
            help_text=_('Please add a brief description of the event.'),
            label=_('Description'))
    place = forms.CharField(max_length=200,widget=forms.HiddenInput(),required=False,
            help_text=_('Please indicate the location of the event.'),
            label=_('Place'))
    country = forms.CharField(max_length=50,widget=forms.HiddenInput(),required=False)
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}),
            label=_('Start date'))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}),
            help_text=_('Please indicate the start and end dates of the event.'),
            label=_('End date'))
    hour = forms.TimeField(widget=forms.TextInput(attrs={'type': 'time'}), required=False,
            help_text=_('Please indicate the start time of the event.'),
            label=_('Hour'))
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.all_timezones], required=False, widget=forms.Select(attrs={'class' : 'form-control'}))
    language = forms.ChoiceField(choices=[
        ('NL', 'Dutch'),
        ('EN', 'English'),
        ('ET', 'Estonian'),
        ('FR', 'Français'),
        ('DE', 'German'),
        ('EL', 'Greek'),
        ('HU', 'Hungarian'),
        ('IT', 'Italian'),
        ('LT', 'Lituanian'),
        ('PT', 'Portuguese'),
        ('ES', 'Spanish'),
        ('SV', 'Swedish'),
        ('OT', 'Other'),
    ], initial='EN', widget=forms.Select(attrs={'class' : 'form-control'}), help_text=_('Please indicate the language of the event.'), label=_('Language'))   
    url = forms.CharField(max_length=200, label=_('URL'),widget=forms.TextInput(),required=False,
            help_text=_('Please provide a URL to an external web site for the event.'))
    latitude = forms.DecimalField(max_digits=9, decimal_places=6, widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, widget=forms.HiddenInput())

    event_type = forms.ChoiceField(
        choices=EVENT_TYPE_CHOICES,
        widget=forms.Select(),
        help_text=_('Please indicate if the event is online or physical.'),
        label=_('Event type'),
        required=True
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Project,
            search_fields=['name__icontains', ]),
        help_text=_(
            'If this event is associated with a project, please select it. If not listed, '
            'please add it <a href="/newProject" target="_blank">here</a> '
            'before submitting the event'),
        label=_('Associated project'),
        required=False
    )
    mainOrganisation = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Organisation,
            search_fields=['name__icontains', ]),
        help_text=_(
            'Please select the organisation coordinating the event. If not listed, '
            'please add it <a href="/new_organisation" target="_blank">here</a> '
            'before submitting the event'),
        label=_('Lead organisation / coordinator'),
        required=False)

    organisations = forms.ModelMultipleChoiceField(
        queryset=Organisation.objects.all(),
        widget=s2forms.ModelSelect2MultipleWidget(
            model=Organisation,
            search_fields=['name__icontains']),
        help_text=_(
            'Please select other organisation(s) participating in the event. If not listed,'
            'please add it <a href="/new_organisation" target="_blank">here</a> '
            'before submitting the event'),
        label=_("Other Organisations"),
        required=False)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
                event_type = 'online' if instance.online_event else 'physical'
                kwargs['initial'] = kwargs.get('initial', {})
                kwargs['initial']['event_type'] = event_type
        super().__init__(*args, **kwargs)
    
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
            event.country = self.data['country']
            event.start_date = self.data['start_date']
            event.end_date = self.data['end_date']
            event.hour = hour
            event.timezone=self.data['timezone']
            event.language=self.data['language']
            event.url = self.data['url']
            event.event_type = self.data['event_type']
            event.latitude = self.data['latitude']
            event.longitude = self.data['longitude']
            event.creator=args.user
            event.project = self.cleaned_data['project']
            event.mainOrganisation = self.cleaned_data['mainOrganisation']
            event.organisations.set(self.cleaned_data['organisations'])
        else:
            event = Event(
                title=self.data['title'],
                description=self.data['description'],
                place=self.data['place'],
                country=self.data['country'],
                start_date=self.data['start_date'],
                end_date=self.data['end_date'],
                hour=hour,
                timezone=self.data['timezone'],
                language=self.data['language'],
                url=self.data['url'],
                latitude=self.data['latitude'],
                longitude=self.data['longitude'],
                event_type=self.data['event_type'],
                creator=args.user
            )
            event.save()
            event.project = self.cleaned_data['project']
            event.mainOrganisation = self.cleaned_data['mainOrganisation']
            event.organisations.set(self.cleaned_data['organisations'])

        event.save()
