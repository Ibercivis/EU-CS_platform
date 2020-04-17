from __future__ import unicode_literals
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.contrib.auth import get_user_model
from . import models
from django_select2.forms import Select2MultipleWidget

User = get_user_model()


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(Field("name"))

    class Meta:
        model = User
        fields = ["name"]


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field("picture"),
            Field("title"),
            Field("bio"),
            Field("institution"),
            Field("interestAreas"),
            Field("choices"),
            Field("latitude"),
            Field("longitude"),
            Submit("update", "Update", css_class="btn-green"),
        )

    CHOICES = ()
    choices = forms.CharField(widget=forms.HiddenInput(),required=False, initial=CHOICES)
    interestAreas = forms.MultipleChoiceField(choices=CHOICES, widget=Select2MultipleWidget,
                        required=False, label="Interest Areas")
    latitude = forms.DecimalField(widget=forms.HiddenInput(),max_digits=9,decimal_places=6,required=False)
    longitude = forms.DecimalField(widget=forms.HiddenInput(),max_digits=9,decimal_places=6,required=False)

    class Meta:
        model = models.Profile
        fields = ["picture", "title", "bio", "institution", "interestAreas", "choices",
                "latitude", "longitude"]


    def save(self, args):
        pForm = super(ProfileForm, self).save(commit=False)
        pForm.user = args.user
        pForm.save()

        choices = self.data['choices']
        choices = choices.split(',')
        for choice in choices:
            if(choice != ''):
                models.InterestArea.objects.get_or_create(interestArea=choice)
        areas = models.InterestArea.objects.all()
        areas = areas.filter(interestArea__in = choices)
        pForm.interestAreas.set(areas)

        return 'success'
