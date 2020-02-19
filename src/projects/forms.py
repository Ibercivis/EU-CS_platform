from django import forms
from django.db import models
from .models import Project, Topic, Status, Keyword
from django.shortcuts import get_object_or_404
from django_select2.forms import Select2MultipleWidget
from django.core.files import File
from PIL import Image

class ProjectForm(forms.Form):
    error_css_class = 'form_error'
    #Basic Project Information
    project_name = forms.CharField(max_length=100)
    aim = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), max_length=300)
   
    CHOICES = ()     

    choices = forms.CharField(widget=forms.HiddenInput(),required=False, initial=CHOICES)    
    keywords = forms.MultipleChoiceField(choices=CHOICES, widget=Select2MultipleWidget, required=False)   

    status = forms.ModelChoiceField(queryset=Status.objects.all())
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)  
    
    topic = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=Select2MultipleWidget, required=False)
    
    #Images and communications
    url = forms.CharField(max_length=200, required=False)
    image = forms.ImageField(required=False)
    x = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)


    image_credit = forms.CharField(max_length=200, required=False)
    #Geography
    latitude = forms.DecimalField(max_digits=9,decimal_places=6)
    longitude = forms.DecimalField(max_digits=9,decimal_places=6)
    #Personal and Organizational Affiliates
    host = forms.CharField(max_length=100)
    #Supplementary information for Citizen Science
    how_to_participate = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), max_length=300, required=False)
    equipment = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), max_length=200, required=False)

    
    contact_person_phone = forms.CharField(max_length=100, required=False)
    

    def clean(self):
        start_date = self.data['start_date']
        end_date = self.data['end_date'] 
        if end_date is not '' and end_date < start_date:
            msg = u"End date should be greater than start date."            
            self._errors["end_date"] = self.error_class([msg])

    def save(self, args, photo):
        start_dateData = self.data['start_date']
        end_dateData = self.data['end_date']        
        pk = self.data.get('projectID', '')        
      
        status = get_object_or_404(Status, id=self.data['status'])
        if(pk):
            project = get_object_or_404(Project, id=pk)
            project.name = self.data['project_name']
            project.url = self.data['url']
            project.start_date = start_dateData
            project.end_date = end_dateData
            project.latitude = self.data['latitude']
            project.longitude = self.data['longitude']
            project.aim = self.data['aim']
            project.description = self.data['description']         
            project.status = status
            project.host = self.data['host']
            
        
        else:           
            project = Project(name = self.data['project_name'], url = self.data['url'],
                         start_date = start_dateData, end_date = end_dateData, creator=args.user,
                         latitude = self.data['latitude'], longitude = self.data['longitude'],
                         aim = self.data['aim'], description = self.data['description'], 
                         status = status, host = self.data['host'])

        if(photo != '/'):
            project.image = photo
        project.save()
        project.topic.set(self.data.getlist('topic'))

        choices = self.data['choices']
        choices = choices.split(',')
        for choice in choices:
            if(choice != ''):
                keyword = Keyword.objects.get_or_create(keyword=choice)                   
        keywords = Keyword.objects.all()
        keywords = keywords.filter(keyword__in = choices)
        project.keywords.set(keywords)

        return 'success'
