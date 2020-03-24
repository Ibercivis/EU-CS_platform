from django import forms
from django.db import models
from .models import Project, Topic, Status, Keyword, FundingBody, FundingAgency, CustomField
from django.shortcuts import get_object_or_404
from django_select2.forms import Select2MultipleWidget, Select2Widget
from django.core.files import File
from django.forms import formset_factory
from PIL import Image
from geopy.geocoders import Nominatim
from django_summernote.widgets import SummernoteWidget
from itertools import chain

geolocator = Nominatim(timeout=None)

class ProjectForm(forms.Form):
    error_css_class = 'form_error'
    #Basic Project Information
    project_name = forms.CharField(max_length=200)
    aim = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 2000}}), label="Aim of the project (max 2000 characters)")
    description = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 3000}}), label="Project description (max 3           000 characters)")
    choices = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    choicesSelected = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    keywords = forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False,label="Keywords (Select or write a new ones, comma separated)")
    status = forms.ModelChoiceField(queryset=Status.objects.all(), label="Status (Select one)")
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    topic = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=Select2MultipleWidget, required=False,label="Topic (Multiple selection)")
    url = forms.CharField(max_length=200, required=False)
    #Contact person info
    contact_person = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'autocomplete':'nope'}))
    contact_person_email = forms.EmailField()
    contact_person_phone = forms.CharField(max_length=100, required=False)
    #Images and communications
    image1 = forms.ImageField(required=False,label="Image 1 (Will be resized to 600x400 pixels)")
    x1 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width1 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    image_credit1 = forms.CharField(max_length=300, required=False, label="Image 1 credit")
    image2 = forms.ImageField(required=False, label="Image 2: Logo (Will be resized to 600x400 pixels)")
    x2 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width2 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    image_credit2 = forms.CharField(max_length=300, required=False, label="Logo credit")
    image3 = forms.ImageField(required=False, label="Image 3: Header (Will be resized to 1100x300 pixels" )
    x3 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y3 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width3 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height3 = forms.FloatField(widget=forms.HiddenInput(), required=False, label="Image 3 credit")
    image_credit3 = forms.CharField(max_length=300, required=False)
    #Geography
    latitude = forms.DecimalField(max_digits=9,decimal_places=6)
    longitude = forms.DecimalField(max_digits=9,decimal_places=6)
    #Personal and Organizational Affiliates
    host = forms.CharField(max_length=100, label="Name of the institution hosting the project")
    #Supplementary information for Citizen Science
    how_to_participate = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 1000}}), required=False, label="How to participate in the project (max 1000 characters)")
    equipment = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 1000}}), required=False, label="Equipment needeed to participate (max 1000 characters)")
    #Funding
    funding_body =  forms.ModelMultipleChoiceField(queryset=FundingBody.objects.all(), widget=Select2MultipleWidget, required=False, label="Funding bodies (Select or write new one)")
    fundingBodySelected = forms.CharField(widget=forms.HiddenInput(), max_length=100, required=False)
    funding_program = forms.CharField(max_length=500, required=False)
    funding_agency =   forms.ModelMultipleChoiceField(queryset=FundingAgency.objects.all(), widget=Select2MultipleWidget, required=False, label="Funding agency (Select or write new one)")
    fundingAgencySelected = forms.CharField(widget=forms.HiddenInput(), max_length=100, required=False)
    #Custom fields
    title = forms.CharField(max_length=100, required=False)
    paragraph = forms.CharField(widget=SummernoteWidget(), required=False)

    def clean(self):
        start_date = self.data['start_date']
        end_date = self.data['end_date']
        if start_date is not '' and end_date is not '' and end_date < start_date:
            msg = u"End date should be greater than start date."
            self._errors["end_date"] = self.error_class([msg])

    def save(self, args, images, cFields):
        pk = self.data.get('projectID', '')
        start_dateData = self.data['start_date']
        end_dateData = self.data['end_date']
        latitude = self.data['latitude']
        longitude = self.data['longitude']
        country = getCountryCode(latitude,longitude).upper()
        status = get_object_or_404(Status, id=self.data['status'])

        if(pk):
            project = get_object_or_404(Project, id=pk)
            project.name = self.data['project_name']
            project.url = self.data['url']
            project.author = self.data['contact_person']
            project.author_email = self.data['contact_person_email']
            project.latitude = latitude
            project.longitude = longitude
            project.country = country
            project.aim = self.data['aim']
            project.description = self.data['description']
            project.status = status
            project.host = self.data['host']
            project.imageCredit1 = self.data['image_credit1']
            project.imageCredit2 = self.data['image_credit2']
            project.imageCredit3 = self.data['image_credit3']
            project.howToParticipate = self.data['how_to_participate']
            project.equipment = self.data['equipment']
            project.fundingProgram = self.data['funding_program']
        else:
            project = Project(name = self.data['project_name'],
                         url = self.data['url'], creator=args.user,
                         author = self.data['contact_person'], author_email = self.data['contact_person_email'],
                         latitude = latitude, longitude = longitude, country = country,
                         aim = self.data['aim'], description = self.data['description'],
                         status = status, host = self.data['host'], imageCredit1 = self.data['image_credit1'],
                         imageCredit2 = self.data['image_credit2'], imageCredit3 = self.data['image_credit3'],
                         howToParticipate = self.data['how_to_participate'],
                         equipment = self.data['equipment'],fundingProgram = self.data['funding_program'] )
        if start_dateData:
            project.start_date = start_dateData
        if end_dateData:
            project.end_date = end_dateData

        fundingBodySelected = self.data['fundingBodySelected']
        if(fundingBodySelected != ''):
            body, exist = FundingBody.objects.get_or_create(body=fundingBodySelected)
            project.fundingBody = body

        fundingAgencySelected = self.data['fundingAgencySelected']
        if(fundingAgencySelected != ''):
            agency, exist = FundingAgency.objects.get_or_create(agency=fundingAgencySelected)
            project.fundingAgency = agency


        if(images[0] != '/'):
            project.image1 = images[0]

        if(images[1] != '/'):
            project.image2 = images[1]

        if(images[2] != '/'):
            project.image3 = images[2]

        if(cFields):
            paragraphs = []
            for cField in cFields:
                paragraphs.append(cField.paragraph)
                CustomField.objects.get_or_create(title=cField.title, paragraph=cField.paragraph)
            cfields = CustomField.objects.all().filter(paragraph__in = paragraphs)
            project = get_object_or_404(Project, id=pk)
            project.customField.set(cfields)
        project.save()
        project.topic.set(self.data.getlist('topic'))
        choices = self.data['choices']
        choices = choices.split(',')
        for choice in choices:
            if(choice != ''):
                keyword = Keyword.objects.get_or_create(keyword=choice)
        keywords = Keyword.objects.all()
        keywords = keywords.filter(keyword__in = choices)
        project.keywords.set(keywords)

        return 'success'


def getCountryCode(latitude, longitude):
    location = geolocator.reverse([latitude, longitude], exactly_one=True)
    if len(location.raw) > 1:
        return location.raw['address']['country_code']
    else:
        return ''


class CustomFieldForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    paragraph = forms.CharField(widget=SummernoteWidget(), required=False)

CustomFieldFormset = formset_factory(CustomFieldForm,extra=1)


class ProjectPermissionForm(forms.Form):
    selectedUsers = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersCollection = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersAllowed =   forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False, label="Allow users to edit")
