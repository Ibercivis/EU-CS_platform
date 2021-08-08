from django import forms
from django_select2.forms import Select2MultipleWidget
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from .models import Organisation, OrganisationType
from projects.forms import getCountryCode
from ckeditor.widgets import CKEditorWidget


class OrganisationForm(forms.Form):

    name = forms.CharField(
            max_length=200,
            help_text=_('The name or the organisation'),
            widget=forms.TextInput())
    url = forms.URLField(
            max_length=200,
            help_text=_('URL of the organisation'),
            widget=forms.TextInput())
    description = forms.CharField(
            help_text=_('Please briefly describe the organisation (max 3000 characters)'),
            widget=CKEditorWidget(config_name='frontpage'),
            max_length=3000)
    orgType = forms.ModelChoiceField(
            queryset=OrganisationType.objects.all(),
            label=_("Type"),
            help_text='Select One',
            widget=forms.Select(attrs={'class': 'js-example-basic-single'}))
    logo = forms.ImageField(
            required=False,
            help_text=_('Please upload the logo of your organisation (.jpg or .png)'),
            widget=forms.FileInput)
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)
    contact_point = forms.CharField(
            max_length=100,
            help_text=_('Please name the contact person or contact point for the organisation'),
            widget=forms.TextInput())
    contact_point_email = forms.EmailField(
            max_length=100,
            help_text=_(
                'Please provide the email address of the contact person or'
                'contact point. Note you will need permission to do that'),
            widget=forms.TextInput())
    latitude = forms.DecimalField(max_digits=9, decimal_places=6, widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, widget=forms.HiddenInput())

    def save(self, args, logo_path):
        pk = self.data.get('organisationID', '')
        orgType = get_object_or_404(OrganisationType, id=self.data['orgType'])
        if(pk):
            organisation = get_object_or_404(Organisation, id=pk)
            organisation.name = self.data['name']
            organisation.url = self.data['url']
            organisation.description = self.data['description']
            organisation.orgType = orgType
            organisation.contactPoint = self.data['contact_point']
            organisation.contactPointEmail = self.data['contact_point_email']
            organisation.latitude = self.data['latitude']
            organisation.longitude = self.data['longitude']
        else:
            organisation = Organisation(
                    name=self.data['name'],
                    url=self.data['url'],
                    creator=args.user,
                    latitude=self.data['latitude'],
                    longitude=self.data['longitude'],
                    description=self.data['description'],
                    orgType=orgType,
                    contactPoint=self.data['contact_point'],
                    contactPointEmail=self.data['contact_point_email'])

        # TODO: Fix this
        if len(logo_path):
            organisation.logo = logo_path
        country = getCountryCode(organisation.latitude, organisation.longitude).upper()
        organisation.country = country
        organisation.save()
        return organisation


class OrganisationPermissionForm(forms.Form):
    selectedUsers = forms.CharField(widget=forms.HiddenInput(), required=False, initial=())
    usersCollection = forms.CharField(widget=forms.HiddenInput(), required=False, initial=())
    usersAllowed = forms.MultipleChoiceField(
            choices=(),
            widget=Select2MultipleWidget,
            required=False,
            label=_("Give additional users permission to edit"))
