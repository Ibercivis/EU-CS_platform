from __future__ import unicode_literals
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.contrib.auth import get_user_model
from . import models
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2MultipleWidget
from organisations.models import Organisation

User = get_user_model()


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(Field("name"))
        self.helper.layout = Layout(Field("email"))

    class Meta:
        model = User
        fields = ["name", "email"]


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field("picture"),
            Field("title"),
            Field("bio"),
            Field("orcid"),
            Field("interestAreas"),
            Field("choices"),
            Field("latitude"),
            Field("longitude"),
            Field("lastname"),
            Field("city"),
            Field("country"),
            Field("postal_code"),
            Submit("update", "Update", css_class="btn-green"),
        )

    CHOICES = ()
    choices = forms.CharField(widget=forms.HiddenInput(),required=False, initial=CHOICES)
    interestAreas = forms.MultipleChoiceField(choices=CHOICES, widget=Select2MultipleWidget,
                        required=False, label="Interest Areas",help_text=_('Please write or select interest areas, separated by commas or pressing enter'))
    latitude = forms.DecimalField(widget=forms.HiddenInput(),max_digits=9,decimal_places=6,required=False)
    longitude = forms.DecimalField(widget=forms.HiddenInput(),max_digits=9,decimal_places=6,required=False)
    organisation = forms.ModelMultipleChoiceField(queryset=Organisation.objects.all(), widget=Select2MultipleWidget(attrs={'data-placeholder':'Related organisations'}), required=False,label="Organisation (Multiple selection)")
    lastname = forms.CharField(label=_("Last name"))

    class Meta:
        model = models.Profile
        fields = ["picture", "title", "bio", "orcid", "interestAreas", "choices", "organisation",
                "latitude", "longitude", "lastname", "city", "country", "postal_code"]


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
        pForm.organisation.set(self.data.getlist('organisation'))
        return 'success'
