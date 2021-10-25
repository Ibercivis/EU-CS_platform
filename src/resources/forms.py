from ckeditor.widgets import CKEditorWidget
from django import forms
from django.shortcuts import get_object_or_404
from django_select2.forms import Select2MultipleWidget
from django_select2 import forms as s2forms
from .models import Resource, Keyword, Category, Audience, Theme, ResourceGroup
from .models import ResourcesGrouped, EducationLevel, LearningResourceType
from authors.models import Author
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from organisations.models import Organisation
from projects.models import Project


class ResourceForm(forms.Form):
    # Main information
    name = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            help_text=_('Insert here the title or name of the resource'))

    url = forms.URLField(
            widget=forms.TextInput(),
            help_text=_(
                'URL to where the document is hosted by the publisher,'
                'or in a permanent repository such as Zenodo, OSF, the RIO Journal, or similar'))
    keywords = forms.ModelMultipleChoiceField(
            queryset=Keyword.objects.all(),
            widget=s2forms.ModelSelect2TagWidget(
                search_fields=['keyword__icontains'],
                attrs={
                    'data-token-separators': '[","]'}),
            help_text=_(
                'Please write or select keywords to describe the resource,'
                '<b>separated by commas or pressing enter</b>'),
            required=True)

    abstract = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_('Please briefly describe the resource (ideally in 500 words or less)'),
            max_length=3000)

    description_citizen_science_aspects = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            help_text=_(
                'Please describe the link between citizen science and the resource you are uploading'
                '– for guidance see the <a href="https://zenodo.org/communities/citscicharacteristics">'
                'ECSA Characteristics of Citizen Science</a> as well as the <a href="https://osf.io/xpr2n/">'
                'ECSA 10 Principles of Citizen Science</a>. What you introduce in this text field will not'
                'appear on the platform; it is just for moderation purposes and for the administrators of'
                'the platform to see.'),
            max_length=2000,
            label=_('Description of Citizen Science Aspects'))

    authors = forms.ModelMultipleChoiceField(
            queryset=Author.objects.all(),
            widget=s2forms.ModelSelect2TagWidget(
                search_fields=['author__icontains'],
                attrs={
                    'data-token-separators': '[","]'}),
            help_text=_(
                'Author(s) of the resource. Enter <i>FirstInitial LastName</i> and close with a comma or'
                ' pressing enter to add an author or multiple authors'),
            required=False,
            label=_("Authors"))

    # To clasify
    # TODO: Improve category
    category = forms.ModelChoiceField(
            queryset=Category.objects.filter(parent__isnull=True),
            help_text=_('Select one of the proposed categories'))
    choices = forms.CharField(widget=forms.HiddenInput(), required=False)
    categorySelected = forms.CharField(widget=forms.HiddenInput(), required=False)

    audience = forms.ModelMultipleChoiceField(
            queryset=Audience.objects.all(),
            widget=Select2MultipleWidget(),
            help_text=_(
                'Select the audience(s) for which the resource is intended.'
                'Multiple options can be selected'))

    theme = forms.ModelMultipleChoiceField(
            queryset=Theme.objects.all(),
            widget=Select2MultipleWidget(),
            help_text=_('The thematic content of the resource (select as many as apply)'))

    resource_DOI = forms.CharField(
            max_length=100,
            required=False,
            widget=forms.TextInput(),
            help_text=_('Please provide the <b>Digital Object Signifier</b> that is unique to your'
                        ' resource'),
            label=_('Resource DOI'))

    # TODO: Change this to be a year field
    year_of_publication = forms.IntegerField(
            required=False,
            widget=forms.TextInput(),
            help_text=_('Enter the year (YYYY) that this version of the resource was published'))

    license = forms.CharField(
            max_length=100,
            widget=forms.TextInput(attrs={'autocomplete': 'nope'}),
            help_text=_('Indicate the resource license, such as Creative Commons CC-BY.'
                        'Enter a URL link to the license if available.'),
            required=False)

    # Linking
    organisation = forms.ModelMultipleChoiceField(
            queryset=Organisation.objects.all(),
            widget=s2forms.ModelSelect2MultipleWidget(
                model=Organisation,
                search_fields=['name__icontains']),
            help_text=_(
                'Organisation(s) contributing the resource (multiple selection separated by comma'
                'or pressing enter). If not listed, please add them <a href="/new_organisation" '
                'target="_blank">here</a > before submitting'),
            required=False,
            label=_("Organisation(s)"))

    project = forms.ModelMultipleChoiceField(
            queryset=Project.objects.all(),
            widget=s2forms.ModelSelect2MultipleWidget(
                model=Project,
                search_fields=['name__icontains']),
            help_text=_(
                'Project(s) where the resource was created (multiple selection separated by comma'
                'or pressing enter). If not listed, please add them <a href="/newProject" '
                'target="_blank">here</a > before submitting'),
            required=False,
            label=_("Project(s)"))

    publisher = forms.CharField(
            max_length=100,
            widget=forms.TextInput(),
            help_text=_('The publisher of the resource'),
            required=False)

    # Images

    image1 = forms.ImageField(
            required=False,
            widget=forms.FileInput,
            label=_("Resource image for the thumbnail profile"),
            help_text=_("This image will be resized to 600x400 pixels"))
    image_credit1 = forms.CharField(max_length=300, required=False, label=_("Image 1 credit"))
    x1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withImage1 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)

    image2 = forms.ImageField(
            required=False,
            widget=forms.FileInput,
            label=_("Resource image for the profile heading"),
            help_text=_("This image will be resized to 1100x400 pixels"))
    image_credit2 = forms.CharField(max_length=300, required=False, label=_("Image 2 credit"))
    x2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withImage2 = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)

    # Curated list
    curatedList = forms.ModelMultipleChoiceField(
            queryset=ResourceGroup.objects.all(),
            widget=Select2MultipleWidget,
            required=False,
            label=_("Curated lists"))

    # Training resources fields
    education_level = forms.ModelMultipleChoiceField(
            queryset=EducationLevel.objects.all(),
            widget=s2forms.ModelSelect2TagWidget(
                search_fields=['educationLevel__icontains'],
                ),
            label=_("Educational level"),
            help_text=_(
                'Insert education level needed, end using comma or pressing enter. '
                'Examples of educational levels include beginner, intermediate or advanced, '
                'and formal sets of level indicators'),
            required=False,
            )
    learning_resource_type = forms.ModelMultipleChoiceField(
            queryset=LearningResourceType.objects.all(),
            widget=s2forms.ModelSelect2TagWidget(
                search_fields=['learningResourceType__icontains'],
                ),
            label=_("Learning resource type"),
            help_text=_(
                'The predominant type or kind characterizing the learning resource. '
                'For example, presentation, handout, etc.'),
            required=False,
            )
    time_required = forms.FloatField(required=False, help_text=_('Aproximate hours required to finish the training'))
    conditions_of_access = forms.CharField(required=False, help_text=_(
        'Please describe any conditions that affect the accessibility of the training material, '
        'such as <i>requires registration</i>, <i>requires enrollment</i>, or <i>requires payment</i>'))

    ''' Save & update a Resource & Training Resource '''
    def save(self, args, images):
        pk = self.data.get('resourceID', '')
        category = get_object_or_404(Category, id=self.data['category'])

        if pk:
            resource = get_object_or_404(Resource, id=pk)
            if resource.hidden:
                resource.hidden = False
            resource.name = self.data['name']
            resource.abstract = self.data['abstract']
            resource.description_citizen_science_aspects = self.data['description_citizen_science_aspects']
            resource.url = self.data['url']
            resource.license = self.data['license']
            resource.publisher = self.data['publisher']
        else:
            resource = self.createResource(args)

        resource.inLanguage = self.data['language']
        resource.resourceDOI = self.data['resource_DOI']
        resource.save()
        if self.data['year_of_publication'] != '':
            resource.datePublished = self.data['year_of_publication']
        else:
            resource.datePublished = None
        resource.category = category

        # Saving images
        if(len(images[0]) > 6):
            resource.image1 = images[0]
        if(len(images[1]) > 6):
            resource.image2 = images[1]
        resource.imageCredit1 = self.data['image_credit1']
        resource.imageCredit2 = self.data['image_credit2']

        # Training resource fields
        isTrainingResource = self.data.get('trainingResource', False)
        if(isTrainingResource):
            resource.educationLevel.set(self.data.getlist('education_level'))
            print(self.data.getlist('learning_resource_type'))
            resource.learningResourceType.set(self.data.getlist('learning_resource_type'))
            if(self.data['time_required'] != ''):
                resource.timeRequired = self.data['time_required']
            resource.conditionsOfAccess = self.data['conditions_of_access']
        # End training resource fields
        resource.save()

        # Set the fields that are lists
        resource.audience.set(self.data.getlist('audience'))
        resource.theme.set(self.data.getlist('theme'))
        resource.organisation.set(self.data.getlist('organisation'))
        resource.project.set(self.data.getlist('project'))
        resource.keywords.set(self.data.getlist('keywords'))
        curatedList = self.data.getlist('curatedList')

        if args.user.is_staff:
            objs = ResourcesGrouped.objects.filter(resource=resource)
            if objs:
                for obj in objs:
                    obj.delete()
            for clist in curatedList:
                resourceGroup = get_object_or_404(ResourceGroup, id=clist)
                ResourcesGrouped.objects.get_or_create(group=resourceGroup, resource=resource)

        return resource.id

    def createResource(self, args):
        return Resource(
                creator=args.user,
                name=self.data['name'],
                url=self.data['url'],
                abstract=self.data['abstract'],
                description_citizen_science_aspects=self.data['description_citizen_science_aspects'],
                license=self.data['license'],
                publisher=self.data['publisher'],
                dateUploaded=datetime.now())


class ResourcePermissionForm(forms.Form):
    selectedUsers = forms.CharField(widget=forms.HiddenInput(), required=False, initial=())
    usersCollection = forms.CharField(widget=forms.HiddenInput(), required=False, initial=())
    usersAllowed = forms.MultipleChoiceField(
            choices=(),
            widget=Select2MultipleWidget,
            required=False,
            label=_("Give additional users permission to edit"))
