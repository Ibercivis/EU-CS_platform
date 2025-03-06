from django import forms

from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from ckeditor.widgets import CKEditorWidget
from django_select2 import forms as s2forms

from .models import Platform

from organisations.models import Organisation
from django_countries import countries
from django.conf import settings


class PlatformForm(forms.Form):
    GEOGRAPHIC_EXTEND_CHOICES = (
        ("GLOBAL", "Global"),
        ("MACRO-REGIONAL", "Macro-regional"),
        ("NATIONAL", "National"),
        ("SUB-NATIONAL", "Sub-national"),
        ("REGIONAL", "Regional"),
        ("CITY", "City"),
        ("NEIGHBOURHOOD", "Neighbourhood"))
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)  # Explicitly store the instance
        super(PlatformForm, self).__init__(*args, **kwargs)

        # Configure translated fields dynamically
        for lang_code in settings.MODELTRANSLATION_LANGUAGES:
            field_name = f'description_{lang_code}'
            self.fields[field_name] = forms.CharField(
                help_text=_('Please briefly describe the network or platform (max 3000 characters).'),
                widget=CKEditorWidget(config_name='frontpage'),
                max_length=3000,
                label=lang_code,
                required=lang_code == settings.MODELTRANSLATION_DEFAULT_LANGUAGE
            )

            # Pre-fill the field with the existing instance value, if present
            if self.instance:
                print("Instance data:", self.instance.__dict__)
                value = getattr(self.instance, field_name, None)
                print(f"Setting initial value for {field_name}: {value}")  # Depuración
                self.fields[field_name].initial = value

    def get_description_fields(self):
        for field_name in self.fields:
            return [self[field_name] for field_name in self.fields if field_name.startswith('description_')]
        
    name = forms.CharField(
        max_length=200,
        help_text=_('Please write the name of the network or platform.'),
        widget=forms.TextInput())

    url = forms.URLField(
        max_length=200,
        label=_('URL'),
        help_text=_('Please provide the URL of the network or platform.'),
        widget=forms.TextInput())

    geographicExtend = forms.ChoiceField(
        label=_('Geographic extent'),
        help_text=_(
            'Please indicate the spatial scale of the network or platform.'),
        choices=GEOGRAPHIC_EXTEND_CHOICES)

    countries = forms.MultipleChoiceField(
        widget=s2forms.Select2MultipleWidget,
        choices=countries,
        help_text=_(
            'Please select the country(ies) related to the network or platform.')
    )
    platformLocality = forms.CharField(
        label=_("Network / platform locality"),
        max_length=300,
        widget=forms.TextInput(),
        required=False,
        help_text=_('Please describe the locality of the network or platform. For example: City of Lisbon.'))

    contactPoint = forms.CharField(
        label=_('Public contact point'),
        max_length=100,
        help_text=_(
            'Please name the contact person or contact point for the network or platform.'),
        widget=forms.TextInput(),
        required=False)

    contactPointEmail = forms.EmailField(
        label=_('Contact point email'),
        max_length=100,
        help_text=_(
            'Please provide the email address of the contact person or '
            'contact point. Note you will need permission to do that.'),
        widget=forms.TextInput(),
        required=False)

    organisation = forms.ModelMultipleChoiceField(
        label=_("Organisation(s)"),
        help_text=_(
            'Please select the organisation(s) coordinating the platform. '
            'If not listed, please add <a href="/new_organisation" '
            'target=_blank">here</a> before submitting the network or platform.'),
        queryset=Organisation.objects.all(),
        widget=s2forms.ModelSelect2MultipleWidget(
            model=Organisation,
            search_fields=['name__icontains']),
        required=False)

    logo = forms.ImageField(
        required=False,
        label=_("Logo of your network or platform"),
        help_text=_('This image will be resized to 600x400 pixels.'),
        widget=forms.FileInput)
    xlogo = forms.FloatField(widget=forms.HiddenInput(), required=False)
    ylogo = forms.FloatField(widget=forms.HiddenInput(), required=False)
    widthlogo = forms.FloatField(widget=forms.HiddenInput(), required=False)
    heightlogo = forms.FloatField(widget=forms.HiddenInput(), required=False)
    logoCredit = forms.CharField(
        max_length=300,
        required=False,
        label=_("Logo credit, if applicable"))

    profileImage = forms.ImageField(
        required=False,
        label=_("Network or platform profile image"),
        help_text=_('This image will be resized to 1100x400 pixels.'),
        widget=forms.FileInput)
    xprofileImage = forms.FloatField(
        widget=forms.HiddenInput(), required=False)
    yprofileImage = forms.FloatField(
        widget=forms.HiddenInput(), required=False)
    widthprofileImage = forms.FloatField(
        widget=forms.HiddenInput(), required=False)
    heightprofileImage = forms.FloatField(
        widget=forms.HiddenInput(), required=False)
    profileImageCredit = forms.CharField(
        max_length=300,
        required=False,
        label=_("Profile image credit, if applicable."))

    ''' Save function '''

    def save(self, request, images):
        if self.instance:  # Update
            platform = self.instance
        else:  # Crate
            platform = Platform(creator=request.user)
        
        # Update fields
        platform.name = self.cleaned_data['name']
        platform.url = self.cleaned_data['url']
        platform.geographicExtend = self.cleaned_data['geographicExtend']
        platform.countries = self.cleaned_data['countries']
        platform.platformLocality = self.cleaned_data['platformLocality']
        platform.contactPoint = self.cleaned_data['contactPoint']
        platform.contactPointEmail = self.cleaned_data['contactPointEmail']
        platform.logoCredit = self.cleaned_data['logoCredit']
        platform.profileImageCredit = self.cleaned_data['profileImageCredit']

        # Manage images
        for key, path in images.items():
            if key == 'logo':
                platform.logo = path
            elif key == 'profileImage':
                platform.profileImage = path
        
        platform.save()  # Save platform first, required for ManyToMany relations

        # Update ManyToMany relations (organisations)
        organisations = self.cleaned_data['organisation']
        platform.organisation.set(organisations)  # Assign the organisations to the platform

        platform.save()  # Save again to ensure consistency
        return platform.id

    ''' Create function '''

    def createPlatfom(self, args):
        platform = Platform(
            creator=args.user,
            name=self.data['name'],
            url=self.data['url'],
            contactPoint=self.data['contactPoint'],
            contactPointEmail=self.data['contactPointEmail'],
            geographicExtend=self.data['geographicExtend'],
            platformLocality=self.data['platformLocality'],
            logoCredit=self.data['logoCredit'],
            profileImageCredit=self.data['profileImageCredit']
        )

        # Manage multilingual descriptions
        for lang_code in settings.MODELTRANSLATION_LANGUAGES:
            field_name = f'description_{lang_code}'
            setattr(platform, f'description_{lang_code}', self.data.get(field_name, '').strip())

        return platform

    ''' Update function '''

    def updatePlatform(self, platform, args):
        platform.name = self.data['name']
        platform.url = self.data['url']
        platform.contactPoint = self.data['contactPoint']
        platform.contactPointEmail = self.data['contactPointEmail']
        platform.geographicExtend = self.data['geographicExtend']
        platform.platformLocality = self.data['platformLocality']
        platform.logoCredit = self.data['logoCredit']
        platform.profileImageCredit = self.data['profileImageCredit']

        # Manage multilingual descriptions
        for lang_code in settings.MODELTRANSLATION_LANGUAGES:
            field_name = f'description_{lang_code}'
            setattr(platform, f'description_{lang_code}', self.data.get(field_name, '').strip())
