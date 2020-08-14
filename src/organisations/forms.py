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
    address = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder':' Please provide the physical address of the organisation'})) 


    def save(self, args, logo_path):        
        orgType = get_object_or_404(OrganisationType, id=self.data['orgType'])

        organisation = Organisation(name = self.data['name'], url = self.data['url'], creator=args.user,                         
                          description = self.data['description'], orgType = orgType, contactPoint = self.data['contact_point'],
                          contactPointEmail = self.data['contact_point_email'], address = self.data['address'])
        
        if(logo_path != '/'):
            organisation.logo_path = logo_path
            
        organisation.save()

        return 'success'
