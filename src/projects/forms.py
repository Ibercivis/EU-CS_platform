from django import forms
from django.db import models
from django.core.files import File
from django.forms import formset_factory
from django.shortcuts import get_object_or_404
from django_select2.forms import Select2MultipleWidget
from django_summernote.widgets import SummernoteWidget
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
from .models import Project, Topic, Status, Keyword, FundingBody, CustomField, OriginDatabase
from organisations.models import Organisation

geolocator = Nominatim(timeout=None)

class ProjectForm(forms.Form):
    #Basic Project Information
    project_name = forms.CharField(max_length=200, \
        widget=forms.TextInput(),help_text='Short name or title of the project')
    
    #aim = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 2000}}), label="Aim of the project (max 2000 characters)")
    aim = forms.CharField(\
        widget=forms.Textarea(), help_text='Primary aim, goal or objective of the project. Max 2000 characters',\
        max_length = 2000)
    
    #description = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 3000}}), label="Description of Citizen Science Aspects (max 3000 characters)")
    description = forms.CharField(\
        widget=forms.Textarea(), help_text='Please describe the citizen science aspect(s) of the project - see the a href="https://zenodo.org/communities/citscicharacteristics">ECSA Characteristics of Citizen Science</a> for guidance',\
        max_length = 3000)
    
    topic = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(),\
        widget=Select2MultipleWidget(), help_text='The project topic(s) or field(s) of science, multiple selection', \
        required=False,label="Science Topic")
    
    keywords = forms.MultipleChoiceField(choices=(), \
        widget=Select2MultipleWidget(), required=False, \
        help_text='Please enter 2-3 keywords (comma separated) to further describe your project and assist search on the platform',label='Keywords')

    status = forms.ModelChoiceField(queryset=Status.objects.all(), label="Activity Status",\
        widget=forms.Select(attrs={'class':'js-example-basic-single'}),help_text='Select one')

    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), \
         required=False, label="Closest approximate start date of the project")

    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), \
       required=False, label="Approximate end date of the project")

    url = forms.CharField(max_length=200, \
        widget=forms.TextInput(), help_text='Please provide a URL to an external web site for the project')

     #Contact Information
    mainOrganisation = forms.ModelChoiceField(queryset=Organisation.objects.all(), \
        widget=forms.Select(attrs={'class':'js-example-basic-single'}), \
        help_text='Organisation coordinating the project. If not listed, please add it <a href="/new_organisation">here</a> \
        before submitting the project', \
        label='Lead Organisation / Coordinator', required=False)

    organisation = forms.ModelMultipleChoiceField(queryset=Organisation.objects.all(), \
        widget=Select2MultipleWidget(), help_text='Other Organisation participanting in the project. If not listed, please add it \
        <a href="/new_organisation">here</a> before submitting the project',\
        required=False,label="Other Organisations")

    choices = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    choicesSelected = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
   
    host = forms.CharField(max_length=100, \
    widget=forms.TextInput(attrs={'placeholder':'Enter the name of the institution hosting or coordinating the project'}),
    required=False)

    contact_person = forms.CharField(max_length=100, \
        widget=forms.TextInput(), \
        help_text='Please name the contact person or contact point for the Project \
        otherwise leave blank', required=False, label="Contact Point")

    contact_person_email = forms.EmailField(required=False, \
        widget=forms.TextInput(), \
        help_text='Please provide the email for the contact person or contact point', \
       label="Contact Point email")

    #Project Profile Images
    image1 = forms.ImageField(required=False,label="Project image for the thumbnail profile",\
        help_text='Will be resized to 600x400 pixels',widget=forms.FileInput)
    x1 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width1 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withImage1 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    image_credit1 = forms.CharField(max_length=300, required=False, label="provide image credit, if applicable")
    
    image2 = forms.ImageField(required=False, label="Project logo",\
        help_text='Will be resized to 600x400 pixels)',widget=forms.FileInput)
    x2 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width2 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withImage2 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    image_credit2 = forms.CharField(max_length=300, required=False, label="provide logo credit, if applicable")
    
    image3 = forms.ImageField(required=False, label="Project image for the profile heading",\
        help_text='Will be resized to 1100x400 pixels', widget=forms.FileInput)
    x3 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y3 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width3 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height3 = forms.FloatField(widget=forms.HiddenInput(), required=False, label="provide image credit, if applicable")
    withImage3 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    image_credit3 = forms.CharField(max_length=300, required=False)
    
    #Participation Information
    #how_to_participate = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 1000}}), required=False, label="How to participate (max 1000 characters)")
    how_to_participate = forms.CharField(widget=forms.Textarea(),\
        help_text='Please describe how people can get involved in the project', max_length = 2000)
    doingAtHome =  forms.BooleanField(required=False,label="Can participate at home")
    
    #equipment = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 1000}}), required=False, label="Project Equipment")
    equipment = forms.CharField(widget=forms.Textarea(),\
        help_text='Describe any required or suggested equipment to be used in the project', max_length = 2000, required=False)
                                         

    #Custom Fields
    title = forms.CharField(max_length=100, required=False)
    paragraph = forms.CharField(widget=SummernoteWidget(), required=False)

    def save(self, args, images, cFields):
        pk = self.data.get('projectID', '')
        start_dateData = self.data['start_date']
        end_dateData = self.data['end_date']
        latitude = self.data['latitude']
        longitude = self.data['longitude']
        country = getCountryCode(latitude,longitude).upper()
        status = get_object_or_404(Status, id=self.data['status'])
        mainOrganisation = get_object_or_404(Organisation, id=self.data['mainOrganisation'])
        doingAtHome=False
        if('doingAtHome' in self.data and self.data['doingAtHome'] == 'on'):
            doingAtHome=True

        if(pk):
            project = get_object_or_404(Project, id=pk)
            if project.hidden:
                project.hidden = False
            self.updateFields(project, latitude, longitude, country, status, doingAtHome, mainOrganisation)
        else:
            project = self.createProject(latitude, longitude, country, status, doingAtHome, mainOrganisation, args)

        if start_dateData:
            project.start_date = start_dateData
        if end_dateData:
            project.end_date = end_dateData

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

        project.organisation.set(self.data.getlist('organisation'))

        choices = self.data['choices']
        choices = choices.split(',')
        for choice in choices:
            if(choice != ''):
                keyword = Keyword.objects.get_or_create(keyword=choice)
        keywords = Keyword.objects.all()
        keywords = keywords.filter(keyword__in = choices)
        project.keywords.set(keywords)

        return 'success'


    def createProject(self, country, status, doingAtHome, mainOrganisation, args):
         return Project(name = self.data['project_name'], url = self.data['url'], creator=args.user,
                         author = self.data['contact_person'], author_email = self.data['contact_person_email'],
                         country = country,
                         aim = self.data['aim'], description = self.data['description'],
                         status = status, imageCredit1 = self.data['image_credit1'],
                         imageCredit2 = self.data['image_credit2'], imageCredit3 = self.data['image_credit3'],
                         howToParticipate = self.data['how_to_participate'],equipment = self.data['equipment'],
                         doingAtHome=doingAtHome, mainOrganisation=mainOrganisation)

    def updateFields(self, project, latitude, longitude, country, status, doingAtHome, mainOrganisation):
        project.name = self.data['project_name']
        project.url = self.data['url']
        project.author = self.data['contact_person']
        project.author_email = self.data['contact_person_email']
        project.country = country
        project.aim = self.data['aim']
        project.description = self.data['description']
        project.status = status
        project.imageCredit1 = self.data['image_credit1']
        project.imageCredit2 = self.data['image_credit2']
        project.imageCredit3 = self.data['image_credit3']
        project.howToParticipate = self.data['how_to_participate']
        project.doingAtHome = doingAtHome
        project.equipment = self.data['equipment']
        project.mainOrganisation = mainOrganisation

class CustomFieldForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    paragraph = forms.CharField(widget=SummernoteWidget(), required=False)

CustomFieldFormset = formset_factory(CustomFieldForm,extra=1)


class ProjectPermissionForm(forms.Form):
    selectedUsers = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersCollection = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersAllowed =   forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False, label="Give additional users permission to edit")
