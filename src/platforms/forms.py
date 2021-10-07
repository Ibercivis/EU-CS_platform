from django import forms

from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget
from django_select2 import forms as s2forms

from organisations.models import Organisation


class PlatformForm(forms.Form):
    GEOGRAPHIC_EXTEND_CHOICES = (
        ("GLOBAL", "Global"),
        ("MACRO-REGIONAL", "Macro-regional"),
        ("NATIONAL", "National"),
        ("SUB-NATIONAL", "Sub-national"),
        ("REGIONAL", "Regional"),
        ("CITY", "City"),
        ("NEIGHBOURHOOD", "Neighbourhood"))



    name = forms.CharField(
            max_length=200,
            help_text=_('The name of the network or plarform'),
            widget=forms.TextInput())

    url = forms.URLField(
            max_length=200,
            help_text=_('URL of the network or platform'),
            widget=forms.TextInput())

    description = forms.CharField(
            max_length=3000,
            help_text=_('Please briefly describe the network or platform (max 3000 characters)'),
            widget=CKEditorWidget(config_name='frontpage'))

    contactPoint = forms.CharField(
            max_length=100,
            help_text=_('Please name the contact person or contact point for the organisation'),
            widget=forms.TextInput(),
            required=False)

    contactPointEmail = forms.EmailField(
            max_length=100,
            help_text=_(
                'Please provide the email address of the contact person or '
                'contact point. Note you will need permission to do that'),
            widget=forms.TextInput(),
            required=False)

    organisation = forms.ModelMultipleChoiceField(
            label=_("Organisation(s)"),
            help_text=_(
                'Organisation(s) contributing the resource (multiple selection separated by comma '
                'or presseing enter. If not listed, please add <a href="/new_organisation" '
                'target=_blank">here</a> before submitting'),
            queryset=Organisation.objects.all(),
            widget=s2forms.ModelSelect2MultipleWidget(
                model=Organisation,
                search_fields=['name__icontains']),
            required=False)

    geographicExtend = forms.ChoiceField(
            help_text=_('Please indicate the spatial scale of the network / platform'),
            choices=GEOGRAPHIC_EXTEND_CHOICES,
            required=False)

    logo = forms.ImageField(
            required=False,
            label=_("Logo of your network or platform"),
            help_text=_('Will be resized to 600x400 pixels'),
            widget=forms.FileInput)

    logoX = forms.FloatField(widget=forms.HiddenInput(), required=False)
    logoY = forms.FloatField(widget=forms.HiddenInput(), required=False)
    logoWidth = forms.FloatField(widget=forms.HiddenInput(), required=False)
    logoHeight = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withLogo = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    logoCredit = forms.CharField(
            max_length=300,
            required=False,
            label=_("Logo credit, if applicable"))

    profileImage = forms.ImageField(
            required=False,
            label=_("Network or platform profile image"),
            help_text=_('Will be resized to 1100x400 pixels)'),
            widget=forms.FileInput)
    profileImageX = forms.FloatField(widget=forms.HiddenInput(), required=False)
    profileImageY = forms.FloatField(widget=forms.HiddenInput(), required=False)
    profileImageWidth = forms.FloatField(widget=forms.HiddenInput(), required=False)
    profileImageHeight = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withProfileImage = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    profileImageCredit = forms.CharField(
            max_length=300,
            required=False,
            label=_("Profile Image credit, if applicable"))
