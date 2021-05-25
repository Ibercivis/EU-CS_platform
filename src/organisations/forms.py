from django import forms
from django_select2.forms import Select2MultipleWidget
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from .models import Organisation, OrganisationType, LEGAL_STATUS, YES_NO
from projects.forms import getCountryCode
from ecsa.models import Delegate
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

User = get_user_model()

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
    origin_name = forms.CharField(label=_("Organization name in the language of origin"), required=False)
    street = forms.CharField(help_text=_("Street address and number"))
    postal_code = forms.IntegerField()
    city = forms.CharField()
    ecsa_billing_street = forms.CharField(label=_("Billing street"))
    ecsa_billing_postal_code = forms.IntegerField(label=_("Billing postal code"))
    ecsa_billing_city = forms.CharField(label=_("Billing city"))
    ecsa_billing_country = forms.CharField(label=_("Billing country"))
    ecsa_billing_email = forms.EmailField(label=_("Billing email"))
    #occupation = models.ForeignKey(OrganisationType, null=True, blank=True, on_delete=models.CASCADE)
    legal_status = forms.ChoiceField(choices=LEGAL_STATUS, required=False)
    has_vat_number = forms.ChoiceField(choices=YES_NO, label=_("Does your organisation have a VAT number?"))
    vat_number = forms.IntegerField(required=False)
    ecsa_reduced_fee = forms.BooleanField(required=False, label=_("Reduced membership (your organisation has less than five full-time employees)"))
    ecsa_old_organisation_fee = forms.BooleanField(required=False, label=_("20% discount as CSA/ACSA member"))
    #Delegates
    main_delegate_name = forms.CharField()
    main_delegate_email = forms.EmailField()
    delegate1_name = forms.CharField(required=False)
    delegate1_email = forms.EmailField(required=False)
    delegate2_name = forms.CharField(required=False)
    delegate2_email = forms.EmailField(required=False)

    def save(self, args, organisationID):
        origin_name = self.data['origin_name']
        street = self.data['street']
        postal_code = self.data['postal_code']
        city = self.data['city']
        ecsa_billing_street = self.data['ecsa_billing_street']
        ecsa_billing_postal_code = self.data['ecsa_billing_postal_code']
        ecsa_billing_city = self.data['ecsa_billing_city']
        ecsa_billing_country = self.data['ecsa_billing_country']
        ecsa_billing_email = self.data['ecsa_billing_email']
        

        organisation = get_object_or_404(Organisation, id=organisationID)
        organisation.origin_name = origin_name
        organisation.street = street
        organisation.postal_code = postal_code
        organisation.city = city
        organisation.ecsa_billing_street = ecsa_billing_street
        organisation.ecsa_billing_postal_code = ecsa_billing_postal_code
        organisation.ecsa_billing_city = ecsa_billing_city
        organisation.ecsa_billing_country = ecsa_billing_country
        organisation.ecsa_billing_email = ecsa_billing_email
        
        if self.data['vat_number'] != '':
            organisation.vat_number = self.data['vat_number']
        else:
            organisation.vat_number = None
        
        organisation.ecsa_reduced_fee=False
        if('ecsa_reduced_fee' in self.data and self.data['ecsa_reduced_fee'] == 'on'):
            organisation.ecsa_reduced_fee=True

        organisation.ecsa_old_organisation_fee=False
        if('ecsa_old_organisation_fee' in self.data and self.data['ecsa_old_organisation_fee'] == 'on'):
            organisation.ecsa_old_organisation_fee=True

        organisation.ecsa_requested_join = True


        main_delegate_name = self.data['main_delegate_name']
        main_delegate_email = self.data['main_delegate_email']
        if(main_delegate_name != '' and main_delegate_email != ''):
            mainDelegate = self.get_or_create_delegate(main_delegate_email, main_delegate_name)                            
            #send email
            if(not organisation.mainDelegate or organisation.mainDelegate.email != main_delegate_email):
                self.sendEmailToDelegate(main_delegate_email, main_delegate_name, organisation.name)
            organisation.mainDelegate = mainDelegate
            
        delegate1_name = self.data['delegate1_name']
        delegate1_email = self.data['delegate1_email']
        if(delegate1_name != '' and delegate1_email != ''):
            delegate1 = self.get_or_create_delegate(delegate1_email, delegate1_name)                              
            #send mail
            if(not organisation.delegate1 or organisation.delegate1.email != delegate1_email):
                self.sendEmailToDelegate(delegate1_email, delegate1_name, organisation.name)
            organisation.delegate1 = delegate1

        delegate2_name = self.data['delegate2_name']
        delegate2_email = self.data['delegate2_email']
        if(delegate2_name != '' and delegate2_email != ''):
            delegate2 = self.get_or_create_delegate(delegate2_email, delegate2_name)                              
            #send mail
            if(not organisation.delegate2 or organisation.delegate2.email != delegate2_email):
                self.sendEmailToDelegate(delegate2_email, delegate2_name, organisation.name)
            organisation.delegate2 = delegate2

        organisation.save()
        return 'success'
    
    def get_or_create_delegate(self, delegate_email, delegate_name):
        delegate, exist = Delegate.objects.get_or_create(email=delegate_email)
        delegate.name = delegate_name
        try:
            user_temp = User.objects.get(email=delegate_email)
        except:
            user_temp = None
        if(user_temp):
            delegate.user = user_temp
        delegate.save()
        return delegate

    def sendEmailToDelegate(self, mail, name, organisation):
        to_email = mail
        subject = 'You have been appointed delegate in an Organisation'
        message = render_to_string('accounts/emails/new_organisation_delegate.html', {'name': name , 'organisation': organisation })
        email = EmailMessage(subject, message, to=[to_email])
        email.content_subtype = "html"
        email.send()


class OrganisationPermissionForm(forms.Form):
    selectedUsers = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersCollection = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersAllowed =  forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False, label=_("Give additional users permission to edit"))