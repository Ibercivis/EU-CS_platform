from __future__ import unicode_literals
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from django.contrib.auth import get_user_model
from . import models
from django.utils.translation import ugettext_lazy as _
from django_select2 import forms as s2forms
from organisations.models import Organisation
from ckeditor.widgets import CKEditorWidget
from django_countries.fields import CountryField


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
            Field("title"),
            Field("surname"),
            Field("country"),
            Field("picture"),
            Field("bio"),
            Field("orcid"),
            Field("interestAreas"),
            Field("latitude"),
            Field("longitude"),
            Submit("update", "Update", css_class="btn-green"),
        )

    bio = forms.CharField(
            widget=CKEditorWidget(config_name='frontpage'),
            max_length=2000,
            required=False)
    interestAreas = forms.ModelMultipleChoiceField(
            queryset=models.InterestArea.objects.all(),
            widget=s2forms.ModelSelect2TagWidget(
                search_fields=['interestArea__icontains'],
                attrs={
                    'data-token-separators': '[","]'}),
            required=False,
            label="Interest Areas",
            help_text=_('Please write or select interest areas, separated by commas or pressing enter'))
    country = CountryField(
            blank_label='(Select country)',
            blank=True).formfield()
    organisation = forms.ModelMultipleChoiceField(
            queryset=Organisation.objects.all(),
            widget=s2forms.ModelSelect2MultipleWidget(
                model=Organisation,
                search_fields=['name__icontains']),
            help_text=_(
                'Other Organisation participating in the project.If not listed,'
                'please add it <a href="/new_organisation" target="_blank">here</a> '
                'before submitting the project'),
            label=_("Other Organisations"),
            required=False)

    class Meta:
        model = models.Profile
        fields = ["picture", "title", "surname", "bio", "orcid", "interestAreas", "organisation"]

    def save(self, args):
        print(self.data)
        pForm = super(ProfileForm, self).save(commit=False)
        pForm.user = args.user
        pForm.interestAreas.set(self.data.getlist('interestAreas'))
        pForm.organisation.set(self.data.getlist('organisation'))
        pForm.country = self.data['country']
        pForm.save()
        return 'success'
