from django import forms
from django_select2.forms import Select2MultipleWidget
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from .models import Organisation, OrganisationType
from projects.forms import getCountryCode

class OrganisationForm(forms.Form):

    name = forms.CharField(max_length=200, help_text=_('The name or the organisation'),
    widget=forms.TextInput())
    url = forms.CharField(max_length=200, help_text=_('URL of the organisation') ,
    widget=forms.TextInput())
    description = forms.CharField(help_text=_('Please briefly describe the organisation (ideally in 500 words or less)'),
    widget=forms.Textarea(), max_length = 3000)
    orgType = forms.ModelChoiceField(queryset=OrganisationType.objects.all(), label=_("Type"),
    help_text='Select One', widget=forms.Select(attrs={'class':'js-example-basic-single'}))
    logo = forms.ImageField(required=False, help_text=_('Please upload the logo of your organisation (.jpg or .png)'),
    label=_("Logo"), widget=forms.FileInput)
    x = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)
    withLogo = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    contact_point = forms.CharField(max_length=100,
    help_text=_('Please name the contact person or contact point for the organisation'),
    widget=forms.TextInput())
    contact_point_email = forms.CharField(max_length=100,
    help_text=_('Please provide the email address of the contact person or contact point. Note you will need permission to do that'),
    widget=forms.TextInput())
    latitude = forms.DecimalField(max_digits=9,decimal_places=6, widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=9,decimal_places=6, widget=forms.HiddenInput())

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
            organisation = Organisation(name = self.data['name'], url = self.data['url'], creator=args.user, latitude=self.data['latitude'],
                    longitude = self.data['longitude'], description = self.data['description'], orgType = orgType, contactPoint = self.data['contact_point'],
                    contactPointEmail = self.data['contact_point_email'])

        if(logo_path != '/'):
            organisation.logo = logo_path


        country = getCountryCode(organisation.latitude,organisation.longitude).upper()
        organisation.country = country

        organisation.save()

        return 'success'


class NewEcsaOrganisationMembershipForm(forms.Form):
    street = forms.CharField(help_text=_("Street address and number"))
    postal_code = forms.IntegerField()
    city = forms.CharField()
    ecsa_billing_street = forms.CharField(label=_("Billing street"))
    ecsa_billing_postal_code = forms.IntegerField(label=_("Billing postal code"))
    ecsa_billing_city = forms.CharField(label=_("Billing city"))
    ecsa_billing_country = forms.CharField(label=_("Billing country"))
    ecsa_billing_email = forms.EmailField(label=_("Billing email"))
    #occupation = models.ForeignKey(OrganisationType, null=True, blank=True, on_delete=models.CASCADE)
    #legal_status = 
    #profit=
    #has_vat_number =
    vat_number = forms.IntegerField(required=False)
    ecsa_reduced_fee = forms.BooleanField(required=False, label=_("Yes, I would like to pay the reduced fee."))
    ecsa_old_organisation_fee = forms.BooleanField(required=False, label=_("Yes, I am a member of CSA or ACSA and would like to get an additional 20% discount."))

class OrganisationPermissionForm(forms.Form):
    selectedUsers = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersCollection = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersAllowed =  forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False, label=_("Give additional users permission to edit"))