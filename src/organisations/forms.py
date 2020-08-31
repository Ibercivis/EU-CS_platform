from django import forms
from django_select2.forms import Select2MultipleWidget
from django.shortcuts import get_object_or_404
from .models import Organisation, OrganisationType

class OrganisationForm(forms.Form):

    name = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'placeholder':'The name of the organisation'}))
    url = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder':'URL of the organisation'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Please briefly describe the organisation (ideally in 500 words or less'}), max_length = 3000)
    orgType = forms.ModelChoiceField(queryset=OrganisationType.objects.all(), label="Type (Select one)", widget=forms.Select(attrs={'class':'js-example-basic-single'}))
    logo = forms.ImageField(required=False,label="Please provide the URL of the logo image for your organisation (.jpg or .png)", widget=forms.FileInput)
    contact_point = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder':'Contact point'}))
    contact_point_email = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder':'Please provide the email address of the contact point for the organisation'}))
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
            
        organisation.save()

        return 'success'
