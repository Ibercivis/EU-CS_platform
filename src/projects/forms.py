from django import forms
from django.db import models
from django.core.files import File
from django.forms import formset_factory
from django.shortcuts import get_object_or_404
from django_select2.forms import Select2MultipleWidget
from django_summernote.widgets import SummernoteWidget
from django.utils.translation import ugettext as _
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
from .models import Project, Topic, Status, Keyword, FundingBody, CustomField, OriginDatabase, ParticipationTask, GeographicExtend
from organisations.models import Organisation

geolocator = Nominatim(timeout=None)

class ProjectForm(forms.Form):
    #Basic Project Information
    project_name = forms.CharField(max_length=200, \
        widget=forms.TextInput(),help_text=_('Short name or title of the project'))
    keywords = forms.MultipleChoiceField(choices=(), \
        widget=Select2MultipleWidget(), required=False, \
        help_text=_('Please enter 2-3 keywords (comma separated) or pressing enter to further describe your project and assist search on the platform'),label=_('Keywords'))

    #aim = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 2000}}), label="Aim of the project (max 2000 characters)")
    aim = forms.CharField(\
        widget=forms.Textarea(), help_text=_('Primary aim, goal or objective of the project. Max 2000 characters'),\
        max_length = 2000)

    #description = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 3000}}), label="Description of Citizen Science Aspects (max 3000 haracters)")
    description = forms.CharField(\
        widget=forms.Textarea(), help_text=_('Please describe the citizen science aspect(s) of the project - see the <a href="https://zenodo.org/communities/citscicharacteristics">ECSA Characteristics of Citizen Science</a> for guidance'),\
        max_length = 3000)
    topic = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(),\
        widget=Select2MultipleWidget(), help_text=_('The project topic(s) or field(s) of science, multiple selection'), \
        required=False,label=_("Topic"))

    participationtask = forms.ModelMultipleChoiceField(queryset=ParticipationTask.objects.all(),\
        widget=Select2MultipleWidget(), help_text=_('Please select the task(s) undertaken by participants'), \
        required=False,label=_("Participation Task"))



    status = forms.ModelChoiceField(queryset=Status.objects.all(), label=_("Activity Status"),\
        widget=forms.Select(attrs={'class':'js-example-basic-single'}),help_text=_('Select one'))

    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), \
        required=False, label=_("Closest approximate start date of the project"))

    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), \
        required=False, label=_("Approximate end date of the project"))

    url = forms.CharField(max_length=200, \
        widget=forms.TextInput(), help_text=_('Please provide a URL to an external web site for the project'))

    geographicextend = forms.ModelMultipleChoiceField(queryset=GeographicExtend.objects.all(),\
        widget=Select2MultipleWidget(),
        help_text=_('Please indicate the spatial scale of the projec'), \
        required=False,label=_("Geographic Extend"))

    projectlocality = forms.CharField(max_length=300, \
        widget=forms.TextInput(), required=False, label= _("Project locality"),
        help_text=_('Please describe the locality of the project, in terms of where the main participant activities take place, \
        E.g. in your backyard, parks in London, rivers in Europe, online globally, etc.'))

    mainOrganisation = forms.ModelMultipleChoiceField(queryset=Organisation.objects.all(), \
        widget=Select2MultipleWidget(), \
        help_text=_('Organisation coordinating the project. If not listed, please add it <a href="/new_organisation">here</a> \
        before submitting the project'), \
        label=_('Lead Organisation / Coordinator'), required=False)

    organisation = forms.ModelMultipleChoiceField(queryset=Organisation.objects.all(), \
        widget=Select2MultipleWidget(), help_text=_('Other Organisation participating in the project. If not listed, please add it \
        <a href="/new_organisation">here</a> before submitting the project'),\
        required=False,label=_("Other Organisations"))

    choices = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())

    #Contact Information
    host = forms.CharField(max_length=100, \
    widget=forms.TextInput(attrs={'placeholder':'Enter the name of the institution hosting or coordinating the project'}),
    required=False)

    contact_person = forms.CharField(max_length=100, \
        widget=forms.TextInput(), \
        help_text=_('Please name the contact person or contact point for the Project'), required=False, label=_("Public Contact Point"))

    contact_person_email = forms.EmailField(required=False, \
        widget=forms.TextInput(), \
        help_text=_('Please provide the email for the contact person or contact point'), label=_("Contact Point Email"))

    #Profile Images
    image1 = forms.ImageField(required=False,label=_("Project image for the thumbnail profile"),\
        help_text=_('Will be resized to 600x400 pixels'),widget=forms.FileInput)
    x1 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width1 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withImage1 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    image_credit1 = forms.CharField(max_length=300, required=False, label=_("provide image credit, if applicable"))
    image2 = forms.ImageField(required=False, label=_("Project Logo"),\
        help_text=_('Will be resized to 600x400 pixels)'),widget=forms.FileInput)
    x2 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width2 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withImage2 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    image_credit2 = forms.CharField(max_length=300, required=False, label=_("provide Logo credit, if applicable"))
    image3 = forms.ImageField(required=False, label=_("Project image for the profile heading"),\
        help_text=_('Will be resized to 1100x400 pixels'), widget=forms.FileInput)
    x3 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y3 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width3 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height3 = forms.FloatField(widget=forms.HiddenInput(), required=False, label=_("provide image credit, if applicable"))
    withImage3 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    image_credit3 = forms.CharField(max_length=300, required=False)

    #Geography
    latitude = forms.DecimalField(max_digits=9,decimal_places=6)
    longitude = forms.DecimalField(max_digits=9,decimal_places=6)

    #Personal and Organizational Affiliates
    #Participation Information
    #how_to_participate = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 1000}}), required=False, label="How to participate (max 1000 characters)")
    how_to_participate = forms.CharField(widget=forms.Textarea(),\
        help_text=_('Please describe how people can get involved in the project'), max_length = 2000)
    doingAtHome =  forms.BooleanField(required=False,label=_("Can participate at home"))
    #equipment = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 1000}}), required=False, label="Project Equipment")

    equipment = forms.CharField(widget=forms.Textarea(),\
        help_text=_('Describe any required or suggested equipment to be used in the project'), max_length = 2000, required=False)
    #Funding
    funding_body =  forms.ModelMultipleChoiceField(queryset=FundingBody.objects.all(), widget=Select2MultipleWidget(),\
        help_text=_('Please enter the funding agencies of the project (e.g. European Commission). \
        Select them from the list or add your own ended by comma or pressing enter'), required=False, label=_("Funding body (Put a comma after each name or pressing enter to add a new funding body)"))
    fundingBodySelected = forms.CharField(widget=forms.HiddenInput(), max_length=100, required=False)

    funding_program = forms.CharField(max_length=500, widget=forms.TextInput(),\
        help_text=_('Indication of the programme that funds or funded a project'),required=False)
    #Origin information
    origin_database =  forms.ModelMultipleChoiceField(queryset=OriginDatabase.objects.all(), widget=Select2MultipleWidget(),\
        help_text=_('Do you know the name of the database where the project first appeared?, add it here ended by comma or pressing enter.'),\
        required=False)
    originDatabaseSelected = forms.CharField(widget=forms.HiddenInput(), max_length=300, required=False)

    originUID = forms.CharField(max_length=200, widget=forms.TextInput(),\
        help_text=_('Do you know the Unique identificator of the project in the previous database?, add it here.'),required=False, \
        label=_("Origin UID"))

    originURL = forms.CharField(max_length=200, widget=forms.TextInput(),\
        help_text=_('Do you know the origin URL in the previous database?, add it here'),required=False, label=_("Origin URL"))

    #Custom fields
    title = forms.CharField(max_length=100, required=False)
    paragraph = forms.CharField(widget=SummernoteWidget(), required=False)

    def save(self, args, images, cFields, mainOrganisationFixed):
        pk = self.data.get('projectID', '')
        start_dateData = self.data['start_date']
        end_dateData = self.data['end_date']
        latitude = self.data['latitude']
        longitude = self.data['longitude']
        projectlocality = self.data['projectlocality']
        country = getCountryCode(latitude,longitude).upper()
        status = get_object_or_404(Status, id=self.data['status'])
        if(mainOrganisationFixed):
            mainOrganisation = get_object_or_404(Organisation, id=mainOrganisationFixed)
        else:
            mainOrganisation = None
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

        fundingBodySelected = self.data['fundingBodySelected']
        if(fundingBodySelected != ''):
            body, exist = FundingBody.objects.get_or_create(body=fundingBodySelected)
            project.fundingBody = body

        originDatabaseSelected = self.data['originDatabaseSelected']
        if(originDatabaseSelected != ''):
            originDatabase, exist = OriginDatabase.objects.get_or_create(originDatabase=originDatabaseSelected)
            project.originDatabase = originDatabase

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
        project.participationtask.set(self.data.getlist('participationtask'))
        project.geographicextend.set(self.data.getlist('geographicextend'))
        project.organisation.set(self.data.getlist('organisation'))

        choices = self.data['choices']
        choices = choices.split(',')
        for choice in choices:
            if(choice != ''):
                keyword = Keyword.objects.get_or_create(keyword=choice)
        keywords = Keyword.objects.all()
        keywords = keywords.filter(keyword__in = choices)
        project.keywords.set(keywords)
        project.save()

        return 'success'


    def createProject(self, latitude, longitude, country, status, doingAtHome, mainOrganisation, args):
         return Project(name = self.data['project_name'], url = self.data['url'], projectlocality = self.data['projectlocality'],
                         creator=args.user,
                         author = self.data['contact_person'], author_email = self.data['contact_person_email'],
                         latitude = latitude, longitude = longitude, country = country,
                         aim = self.data['aim'], description = self.data['description'],
                         status = status, imageCredit1 = self.data['image_credit1'],
                         imageCredit2 = self.data['image_credit2'], imageCredit3 = self.data['image_credit3'],
                         howToParticipate = self.data['how_to_participate'],equipment = self.data['equipment'],
                         fundingProgram = self.data['funding_program'],originUID = self.data['originUID'],
                         originURL = self.data['originURL'], doingAtHome=doingAtHome, mainOrganisation=mainOrganisation)

    def updateFields(self, project, latitude, longitude, country, status, doingAtHome, mainOrganisation):
        project.name = self.data['project_name']
        project.url = self.data['url']
        project.projectlocality = self.data['projectlocality']
        project.author = self.data['contact_person']
        project.author_email = self.data['contact_person_email']
        project.latitude = latitude
        project.longitude = longitude
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
        project.fundingProgram = self.data['funding_program']
        project.originUID = self.data['originUID']
        project.originURL = self.data['originURL']
        project.mainOrganisation = mainOrganisation


def getCountryCode(latitude, longitude):
    try:
        location = geolocator.reverse([latitude, longitude], exactly_one=True)
        if len(location.raw) > 1:
            return location.raw['address']['country_code']
        else:
            return ''
    except GeocoderServiceError:
        return ''


class CustomFieldForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    paragraph = forms.CharField(widget=SummernoteWidget(), required=False)

CustomFieldFormset = formset_factory(CustomFieldForm,extra=1)


class ProjectPermissionForm(forms.Form):
    selectedUsers = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersCollection = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersAllowed =   forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False, label=_("Give additional users permission to edit"))
