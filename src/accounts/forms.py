from __future__ import unicode_literals
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext_lazy as _
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field
from crispy_forms.bootstrap import StrictButton
from authtools import forms as authtoolsforms
from django.contrib.auth import forms as authforms
from django.urls import reverse
from captcha.fields import ReCaptchaField
from organisations.models import OrganisationType

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
        self.fields["ecsa_individual_membership"] = forms.BooleanField(required=False)
        self.fields["lastname"] = forms.CharField()
        self.fields["ecsa_billing_email"] = forms.EmailField(required=False)
        self.fields["ecsa_reduced_fee"] = forms.BooleanField(required=False)
        self.fields["street"] = forms.CharField(required=False)
        self.fields["postal_code"] = forms.IntegerField(required=False)
        self.fields["city"] = forms.CharField(required=False)
        self.fields["country"] = forms.CharField(required=False)
        self.fields["occupation"] = forms.ModelChoiceField(queryset=OrganisationType.objects.all(), required=False)
       # self.fields["captcha"] = ReCaptchaField()
        self.helper.layout = Layout(
            Field("email", placeholder=_("Enter Email"), autofocus=""),
            Field("name", placeholder=_("Enter Full Name")),
            Field("lastname", placeholder=_("Enter Last Name")),
            Field("password1", placeholder=_("Enter Password")),
            Field("password2", placeholder=_("Re-enter Password")),
            Field("ecsa_individual_membership"),
            Field("ecsa_billing_email", placeholder=_("Please provide the email to receive proof of payment here.")),
            Field("ecsa_reduced_fee"),
            Field("street", placeholder=_("Street address and number")),
            Field("postal_code"),
            Field("city"),
            Field("country"),
            Field("occupation"),
     #       Field("captcha"),
            StrictButton(_("Sign up"), css_class="btn-green", type="Submit"),
        )



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
