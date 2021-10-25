from ckeditor.widgets import CKEditorWidget
from django.contrib.gis import forms
from django.shortcuts import get_object_or_404
from django_select2.forms import Select2MultipleWidget
from django_select2 import forms as s2forms
from django_summernote.widgets import SummernoteWidget
from django.utils.translation import ugettext_lazy as _
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
from .models import Project, Topic, Status, Keyword, FundingBody
from .models import ParticipationTask, GeographicExtend, HasTag, DifficultyLevel, TranslatedProject
from organisations.models import Organisation


geolocator = Nominatim(timeout=None)


class ProjectGeographicLocationForm(forms.Form):

    projectGeographicLocation = forms.MultiPolygonField(
            required=False,
            widget=forms.OSMWidget(attrs={}),
            label=_(""))


class ProjectForm(forms.Form):

    # Main information
    project_name = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            help_text=_('Short name or title of the project'))

    url = forms.URLField(
            max_length=200,
            widget=forms.TextInput(),
            help_text=_('Please provide a URL to an external web site for the project'))

    description = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Please provide a description of your project here.'),
            max_length=3000)

    aim = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Primary aim, goal or objective of the project. Max 2000 characters'),
            max_length=2000)

    description_citizen_science_aspects = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Please describe the citizen science aspect(s) of the project and the link of the project to'
                        'citizen science using the <a href="https://zenodo.org/communities/citscicharacteristics">ECSA'
                        'Characteristics of Citizen Science</a> and the <a href="https://osf.io/xpr2n/">ECSA 10 '
                        'Principles of Citizen Science</a>. What you introduce in this text field will not appear '
                        'on the platform; it is just for moderation purposes'),
            max_length=2000,
            label=_('Description of citizen science aspects'))

    status = forms.ModelChoiceField(
           queryset=Status.objects.all(),
           label=_("Activity status"),
           widget=forms.Select(attrs={'class': 'js-example-basic-single'}),
           help_text=_('Select one'))

    keywords = forms.ModelMultipleChoiceField(
            queryset=Keyword.objects.all(),
            widget=s2forms.ModelSelect2TagWidget(
                search_fields=['keyword__icontains'],
                attrs={
                    'data-token-separators': '[","]'}),
            required=True,
            help_text=_('Please enter 2-3 keywords <b>comma separated</b> or pressing enter'),
            label=_('Keywords'))

    # Useful information to classificate the project
    start_date = forms.DateField(
             widget=forms.TextInput(attrs={'type': 'date'}),
             required=False,
             label=_("Closest approximate start date of the project"))

    end_date = forms.DateField(
            widget=forms.TextInput(attrs={'type': 'date'}),
            required=False,
            label=_("Approximate end date of the project"))

    topic = forms.ModelMultipleChoiceField(
            queryset=Topic.objects.all(),
            widget=Select2MultipleWidget(),
            help_text=_('The project topic(s) or field(s) of science, multiple selection'),
            required=False,
            label=_("Topic"))

    hasTag = forms.ModelMultipleChoiceField(
            queryset=HasTag.objects.all(),
            widget=Select2MultipleWidget(),
            help_text=_('More information about participation, multiple selection'),
            required=False,
            label=_("Tags"))

    # Participation information
    participationTask = forms.ModelMultipleChoiceField(
            queryset=ParticipationTask.objects.all(),
            widget=Select2MultipleWidget(),
            help_text=_('Please select the task(s) undertaken by participants'),
            required=False,
            label=_("Participation task"))

    difficultyLevel = forms.ModelChoiceField(
            queryset=DifficultyLevel.objects.all(),
            widget=forms.Select(),
            help_text=_('How difficult is the project?'),
            required=False,
            label=_("Difficulty level"))

    how_to_participate = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Please describe how people can get involved in the project'),
            max_length=2000,
            required=False)

    equipment = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Describe any required or suggested equipment to be used in the project'),
            max_length=2000,
            required=False)

    # Project location
    geographicextend = forms.ModelMultipleChoiceField(
            queryset=GeographicExtend.objects.all(),
            widget=Select2MultipleWidget(),
            help_text=_('Please indicate the spatial scale of the project'),
            required=False,
            label=_("Geographic extend"))

    projectlocality = forms.CharField(
            max_length=300,
            widget=forms.TextInput(),
            required=False,
            label=_("Project locality"),
            help_text=_('Please describe the locality of the project, in terms of where the main participant'
                        'activities take place,<br/> E.g. in your backyard, parks in London, rivers in Europe, '
                        'online globally, etc.'))

    projectGeographicLocation = forms.MultiPolygonField(
            required=False,
            widget=forms.OSMWidget(attrs={}),
            label=_("Project geographic location"))

    # Contact and hosts details
    contact_person = forms.CharField(
            max_length=100,
            widget=forms.TextInput(),
            help_text=_('Please name the contact person or contact point for the Project'),
            required=False,
            label=_("Public contact point"))

    contact_person_email = forms.EmailField(
            required=False,
            widget=forms.TextInput(),
            help_text=_('Please provide the email for the contact person or contact point'),
            label=_("Contact point email"))

    mainOrganisation = forms.ModelChoiceField(
            queryset=Organisation.objects.all(),
            widget=s2forms.ModelSelect2Widget(
                model=Organisation,
                search_fields=['name__icontains', ]),
            help_text=_(
                'Organisation coordinating the project. If not listed, '
                'please add it <a href="/new_organisation" target="_blank">here</a> '
                'before submitting the project'),
            label=_('Lead organisation / coordinator'),
            required=False)

    organisation = forms.ModelMultipleChoiceField(
            queryset=Organisation.objects.all(),
            widget=s2forms.ModelSelect2MultipleWidget(
                model=Organisation,
                search_fields=['name__icontains']),
            help_text=_(
                'Other Organisation participating in the project.If not listed,'
                'please add it <a href="/new_organisation" target="_blank">here</a> '
                'before submitting the project'),
            label=_("Other Organisations"),
            required=False)

    # Funding information
    funding_body = forms.ModelMultipleChoiceField(
            queryset=FundingBody.objects.all(),
            widget=s2forms.Select2TagWidget(
                attrs={'data-token-separators': '[","]'}
            ),
            help_text=_('Please enter the funding agencies of the project (e.g. European Commission)<br />'
                        'Select them from the list or add your own <b>ended by comma or pressing enter</b>'),
            required=False,
            label=_("Funding body"))

    funding_program = forms.CharField(
            max_length=500,
            widget=forms.TextInput(),
            help_text=_('Indication of the programme that funds or funded a project'),
            required=False)

    # Images
    image1 = forms.ImageField(
            required=False,
            label=_("Image for the thumbnail profile"),
            help_text=_('Will be resized to 600x400 pixels'),
            widget=forms.FileInput)

    x1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withImage1 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    image_credit1 = forms.CharField(
            max_length=300,
            required=False,
            label=_("Thumbnail credit, if applicable"))

    image2 = forms.ImageField(
            required=False,
            label=_("Project logo"),
            help_text=_('Will be resized to 600x400 pixels)'),
            widget=forms.FileInput)
    x2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withImage2 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    image_credit2 = forms.CharField(
            max_length=300,
            required=False,
            label=_("Logo credit, if applicable"))

    image3 = forms.ImageField(
            required=False,
            label=_("Image for the profile heading"),
            help_text=_('Will be resized to 1100x400 pixels'),
            widget=forms.FileInput)
    x3 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y3 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width3 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height3 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withImage3 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    image_credit3 = forms.CharField(
            max_length=300,
            required=False,
            label=_("Heading image credit, if applicable"))

    # Others, some of them unused
    host = forms.CharField(
            max_length=100,
            widget=forms.TextInput(
                attrs={'placeholder': 'Enter the name of the institution hosting or coordinating the project'}),
            required=False)
    participatingInaContest = forms.BooleanField(
            required=False,
            label=_('I want to participate in the #MonthOfTheProjects and agree to be contacted via email if the'
                    'project I am submitting wins the contest.'
                    '<a href="/blog/2021/05/31/june-monthoftheprojects-eu-citizenscience/"> Learn more here!</a>'))
    # Custom fields
    title = forms.CharField(max_length=100, required=False)
    paragraph = forms.CharField(widget=SummernoteWidget(), required=False)

    ''' Save function '''
    def save(self, args, images, cFields, mainOrganisationFixed):
        pk = self.data.get('projectID', '')
        start_dateData = self.data['start_date']
        end_dateData = self.data['end_date']
        projectlocality = self.data['projectlocality']
        projectGeographicLocation = self.data['projectGeographicLocation']
        # country = getCountryCode(latitude,longitude).upper()
        status = get_object_or_404(Status, id=self.data['status'])
        if (self.data['difficultyLevel']):
            difficultyLevel = get_object_or_404(DifficultyLevel, id=self.data['difficultyLevel'])
        else:
            difficultyLevel = None
        if (self.data['mainOrganisation']):
            mainOrganisation = get_object_or_404(Organisation, id=self.data['mainOrganisation'])
        else:
            mainOrganisation = None

        doingAtHome = False
        if('doingAtHome' in self.data and self.data['doingAtHome'] == 'on'):
            doingAtHome = True

        participatingInaContest = False
        if('participatingInaContest' in self.data and self.data['participatingInaContest'] == 'on'):
            participatingInaContest = True

        if(pk):
            project = get_object_or_404(Project, id=pk)
            if project.hidden:
                project.hidden = False
            self.updateFields(
                    project,
                    status,
                    difficultyLevel,
                    doingAtHome,
                    mainOrganisation,
                    projectlocality,
                    projectGeographicLocation)
        else:
            project = self.createProject(
                    status,
                    difficultyLevel,
                    doingAtHome,
                    projectGeographicLocation,
                    participatingInaContest,
                    mainOrganisation,
                    projectlocality,
                    args)

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

        project.save()
        project.topic.set(self.data.getlist('topic'))
        project.keywords.set(self.data.getlist('keywords'))
        project.fundingBody.set(self.data.getlist('funding_body'))
        project.participationTask.set(self.data.getlist('participationTask'))
        project.hasTag.set(self.data.getlist('hasTag'))
        project.geographicextend.set(self.data.getlist('geographicextend'))
        project.organisation.set(self.data.getlist('organisation'))

        # TODO: I think not needed, check
        project.save()

        return project.id

    def createProject(
            self,
            status,
            difficultyLevel,
            doingAtHome,
            projectGeographicLocation,
            participatingInaContest,
            mainOrganisation,
            projectLocality,
            args):
        return Project(
                creator=args.user,
                name=self.data['project_name'],
                url=self.data['url'],
                description=self.data['description'],
                description_citizen_science_aspects=self.data['description_citizen_science_aspects'],
                aim=self.data['aim'],
                projectlocality=self.data['projectlocality'],
                mainOrganisation=mainOrganisation,
                author=self.data['contact_person'],
                author_email=self.data['contact_person_email'],
                status=status,
                difficultyLevel=difficultyLevel,
                imageCredit1=self.data['image_credit1'],
                imageCredit2=self.data['image_credit2'],
                imageCredit3=self.data['image_credit3'],
                howToParticipate=self.data['how_to_participate'],
                equipment=self.data['equipment'],
                fundingProgram=self.data['funding_program'],
                # originUID=self.data['originUID'],
                # originURL=self.data['originURL'],
                # doingAtHome=doingAtHome,
                participatingInaContest=participatingInaContest,
                projectGeographicLocation=projectGeographicLocation)

    def updateFields(
            self, project, status, difficultyLevel,
            doingAtHome, mainOrganisation, projectLocality, projectGeographicLocation):
        project.name = self.data['project_name']
        project.url = self.data['url']
        project.projectlocality = self.data['projectlocality']
        project.author = self.data['contact_person']
        project.author_email = self.data['contact_person_email']
        project.aim = self.data['aim']
        project.description = self.data['description']
        project.description_citizen_science_aspects = self.data['description_citizen_science_aspects']
        project.status = status
        project.difficultyLevel = difficultyLevel
        project.imageCredit1 = self.data['image_credit1']
        project.imageCredit2 = self.data['image_credit2']
        project.imageCredit3 = self.data['image_credit3']
        project.howToParticipate = self.data['how_to_participate']
        project.doingAtHome = doingAtHome
        project.equipment = self.data['equipment']
        project.fundingProgram = self.data['funding_program']
        project.mainOrganisation = mainOrganisation
        project.projectGeographicLocation = projectGeographicLocation

        # If there are translations, need to improve them
        project.translatedProject.all().update(needsUpdate=True)


def getCountryCode(latitude, longitude):
    try:
        location = geolocator.reverse([latitude, longitude], exactly_one=True)
        if len(location.raw) > 1:
            return location.raw['address']['country_code']
        else:
            return ''
    except GeocoderServiceError:
        return ''


''' This is the form to translate projects '''


class ProjectTranslationForm(forms.Form):
    translatedDescription = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Please provide a <i>description</i> field translation.'),
            max_length=3000,
            label=_("Description"))

    translatedAim = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Please provide an <i>aim</i> field translation.'),
            max_length=2000,
            label=_("Aim"),
            required=True)

    translatedHowToParticipate = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Please provide a <i>how to participate</i> field translation.'),
            max_length=2000,
            label=_("How to participate"),
            required=False)

    translatedEquipment = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Please provide a <i>translated equipment</i> field translation.'),
            max_length=2000,
            label=_("Needed equipment"),
            required=False)

    def save(self, args):
        project = Project.objects.get(id=self.data.get('projectId'))
        translation = project.translatedProject.filter(inLanguage=self.data.get('languageId')).first()
        if translation:
            TranslatedProject.objects.filter(id=translation.id).delete()
        t1 = TranslatedProject(
                inLanguage=self.data.get('languageId'),
                translatedDescription=self.data.get('translatedDescription'),
                translatedAim=self.data.get('translatedAim'),
                translatedHowToParticipate=self.data.get('translatedHowToParticipate'),
                translatedEquipment=self.data.get('translatedEquipment'),
                needsUpdate=False,
                creator=args.user,
                )
        t1.save()
        project.translatedProject.add(t1)
        project.save()


class CustomFieldForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    paragraph = forms.CharField(widget=SummernoteWidget(), required=False)


class ProjectPermissionForm(forms.Form):
    selectedUsers = forms.CharField(widget=forms.HiddenInput(), required=False, initial=())
    usersCollection = forms.CharField(widget=forms.HiddenInput(), required=False, initial=())
    usersAllowed = forms.MultipleChoiceField(
            choices=(),
            widget=Select2MultipleWidget,
            required=False,
            label=_("Give additional users permission to edit"))
