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
from organisations.models import OrganisationType
from profiles.models import Profile

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
        self.fields["ecsa_individual_membership"] = forms.BooleanField(required=False, label=_("Yes, I would like to become a member of ECSA as an individual."))
        self.fields["name"] = forms.CharField(label=_("First name"))
        self.fields["lastname"] = forms.CharField(label=_("Last name"))
        self.fields["ecsa_billing_email"] = forms.EmailField(required=False)
        self.fields["ecsa_reduced_fee"] = forms.BooleanField(required=False, label=_("Yes, I would like to pay the reduced fee."))
        self.fields["ecsa_old_member_fee"] = forms.BooleanField(required=False, label=_("Yes, I am a member of CSA or ACSA and would like to get an additional 20% discount."))
        self.fields["street"] = forms.CharField(required=False)
        self.fields["postal_code"] = forms.IntegerField(required=False)
        self.fields["city"] = forms.CharField(required=False)
        self.fields["country"] = forms.CharField(required=False)
        self.fields["occupation"] = forms.ModelChoiceField(queryset=OrganisationType.objects.all(), required=False)
       # self.fields["captcha"] = ReCaptchaField()
        self.helper.layout = Layout(
            Field("email", placeholder=_("Enter Email"), autofocus=""),
            Field("name", placeholder=_("Enter first name")),
            Field("lastname", placeholder=_("Enter last name")),
            Field("password1", placeholder=_("Enter password")),
            Field("password2", placeholder=_("Re-enter password")),
            Field("ecsa_individual_membership"),
            Field("ecsa_billing_email", placeholder=_("Please provide the email to receive proof of payment here.")),
            Field("ecsa_reduced_fee"),
            Field("ecsa_old_member_fee"),
            Field("street", placeholder=_("Street address and number")),
            Field("postal_code"),
            Field("city"),
            Field("country"),
            Field("occupation"),
     #       Field("captcha"),
            StrictButton(_("Sign up"), css_class="btn-green", type="Submit"),
        )

class NewEcsaIndividualMembershipForm(forms.Form):
    ecsa_billing_email = forms.EmailField(help_text=_("Please provide the email to receive proof of payment here."))
    ecsa_reduced_fee = forms.BooleanField(required=False, label=_("Yes, I would like to pay the reduced fee."))
    ecsa_old_member_fee = forms.BooleanField(required=False, label=_("Yes, I am a member of CSA or ACSA and would like to get an additional 20% discount."))
    street = forms.CharField(help_text=_("Street address and number"))
    postal_code = forms.IntegerField()
    city = forms.CharField()
    country = forms.CharField()
    occupation = forms.ModelChoiceField(queryset=OrganisationType.objects.all())

    def save(self, args, profileID):
        saveProfile(self, profileID, True)
        return 'success'

def saveProfile(self, profileID, ecsa_individual_membership):
    
    profile = get_object_or_404(Profile, user_id=profileID)
    if(ecsa_individual_membership):
        street = self.data['street']
        postal_code = self.data['postal_code']
        city = self.data['city']
        country = self.data['country']
        ecsa_billing_email = self.data['ecsa_billing_email']
        profile.street = street
        profile.postal_code = postal_code
        profile.city = city
        profile.street = street
        profile.postal_code = postal_code
        profile.city = city
        profile.country = country
        profile.ecsa_billing_email = ecsa_billing_email
        profile.ecsa_reduced_fee=False
        if('ecsa_reduced_fee' in self.data and self.data['ecsa_reduced_fee'] == 'on'):
            profile.ecsa_reduced_fee=True

        profile.ecsa_old_member_fee=False
        if('ecsa_old_member_fee' in self.data and self.data['ecsa_old_member_fee'] == 'on'):
            profile.ecsa_old_member_fee=True

        if('occupation' in self.data and self.data['occupation']):
            profile.occupation = get_object_or_404(OrganisationType, id=self.data['occupation'])
        
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
