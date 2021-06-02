from __future__ import unicode_literals
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field
from crispy_forms.bootstrap import StrictButton
from authtools import forms as authtoolsforms
from django.contrib.auth import forms as authforms
from django.urls import reverse
from captcha.fields import ReCaptchaField
from profiles.models import Profile, Occupation
from django_countries.fields import CountryField

User = get_user_model()

class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["username"].widget.input_type = "email"  # ugly hack

        self.helper.layout = Layout(
            Field("username", placeholder=_("Enter Email"), autofocus=""),
            Field("password", placeholder=_("Enter Password")),
            HTML(
                'Forgot Password? <a href="{}">Remember me</a><br><br>'.format(
                    reverse("accounts:password-reset")
                )
            ),
            StrictButton(_("Log in"), css_class="btn-green", type="Submit")

        )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                try:
                    user_temp = User.objects.get(email=username)
                except:
                    user_temp = None

                if user_temp is not None:
                    if not user_temp.is_active:
                        raise forms.ValidationError(
                            _("We see that your email address is in our database, but that you have not yet confirmed your address. Please search for the confirmation email in your inbox (or spam) to activate your account")
                        )
                    else:
                        raise forms.ValidationError(
                            self.error_messages['invalid_login'],
                            code='invalid_login',
                            params={'username': self.username_field.verbose_name},
                        )

                else:
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                        params={'username': self.username_field.verbose_name},
                    )

        return self.cleaned_data


class SignupForm(authtoolsforms.UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["orcid"] = forms.CharField(required=False)
        self.helper = FormHelper()
        self.fields["email"].widget.input_type = "email"  # ugly hack
        self.fields["ecsa_individual_membership"] = forms.BooleanField(required=False, label=_("I want to become an ECSA member."))
        self.fields["name"] = forms.CharField(label=_("First name"))
        self.fields["lastname"] = forms.CharField(label=_("Last name"))
        self.fields["ecsa_reduced_fee"] = forms.BooleanField(required=False, label=_("50% reduced membership (retired, unemployed or student)"))
        self.fields["ecsa_old_member_fee"] = forms.BooleanField(required=False, label=_("20% discount as CSA/ACSA member"))
        self.fields["ecsa_street"] = forms.CharField(required=False, label=_("Street"))
        self.fields["ecsa_postal_code"] = forms.IntegerField(required=False, label=_("Postal code"))
        self.fields["ecsa_city"] = forms.CharField(required=False, label=_("City"))
        self.fields["ecsa_country"] = CountryField(blank=True).formfield(label=_("Country"))
        self.fields["occupation"] = forms.ModelChoiceField(queryset=Occupation.objects.all(), required=False)
       # self.fields["captcha"] = ReCaptchaField()
        self.helper.layout = Layout(
            Field("email", placeholder=_("Enter Email"), autofocus=""),
            Field("name", placeholder=_("Enter first name")),
            Field("lastname", placeholder=_("Enter last name")),
            Field("password1", placeholder=_("Enter password")),
            Field("password2", placeholder=_("Re-enter password")),
            Field("ecsa_individual_membership"),
            Field("ecsa_reduced_fee"),
            Field("ecsa_old_member_fee"),
            Field("ecsa_street", placeholder=_("Street address and number")),
            Field("ecsa_postal_code"),
            Field("ecsa_city"),
            Field("ecsa_country"),
            Field("occupation"),
     #       Field("captcha"),
            StrictButton(_("Sign up"), css_class="btn-green", type="Submit"),
        )

class NewEcsaIndividualMembershipForm(forms.Form):
    ecsa_reduced_fee = forms.BooleanField(required=False, label=_("Reduced membership (retired, unemployed or student)"))
    ecsa_old_member_fee = forms.BooleanField(required=False, label=_("20% discount as CSA/ACSA member"))
    ecsa_street = forms.CharField(help_text=_("Street address and number"), label=_("Street"))
    ecsa_postal_code = forms.IntegerField(label=_("Postal code"))
    ecsa_city = forms.CharField(label=_("City"))
    ecsa_country = CountryField(blank=True).formfield(label=_("Country"))
    occupation = forms.ModelChoiceField(queryset=Occupation.objects.all())

    def save(self, args, profileID):
        saveProfile(self, profileID, True)
        return 'success'

def saveProfile(self, profileID, ecsa_individual_membership):
    
    profile = get_object_or_404(Profile, user_id=profileID)
    if(ecsa_individual_membership):
        ecsa_street = self.data['ecsa_street']
        ecsa_postal_code = self.data['ecsa_postal_code']
        ecsa_city = self.data['ecsa_city']
        ecsa_country = self.data['ecsa_country']
        profile.ecsa_street = ecsa_street
        profile.ecsa_postal_code = ecsa_postal_code
        profile.ecsa_city = ecsa_city
        profile.ecsa_country = ecsa_country
        profile.ecsa_reduced_fee=False
        if('ecsa_reduced_fee' in self.data and self.data['ecsa_reduced_fee'] == 'on'):
            profile.ecsa_reduced_fee=True

        profile.ecsa_old_member_fee=False
        if('ecsa_old_member_fee' in self.data and self.data['ecsa_old_member_fee'] == 'on'):
            profile.ecsa_old_member_fee=True

        if('occupation' in self.data and self.data['occupation']):
            profile.occupation = get_object_or_404(Occupation, id=self.data['occupation'])
        
        profile.ecsa_requested_join = True

    if('lastname' in self.data and self.data['lastname']):
            profile.lastname = self.data['lastname']
           
    
    profile.save()

class PasswordChangeForm(authforms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("old_password", placeholder=_("Enter old password"), autofocus=""),
            Field("new_password1", placeholder=_("Enter new password")),
            Field("new_password2", placeholder=_("Enter new password (again)")),
            StrictButton(_("Change Password"), css_class="btn-red", type="Submit"),
        )


class PasswordResetForm(authtoolsforms.FriendlyPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field("email", placeholder=_("Enter email"), autofocus=""),
            StrictButton(_("Reset Password"), css_class="btn-red", type="Submit"),
        )
class SetPasswordForm(authforms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field("new_password1", placeholder=_("Enter new password"), autofocus=""),
            Field("new_password2", placeholder=_("Enter new password (again)")),
            Submit("pass_change", _("Change Password"), css_class="btn-red"),
        )
