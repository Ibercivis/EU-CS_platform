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
#from captcha.fields import ReCaptchaField
from django_recaptcha.fields import ReCaptchaField
#from captcha.fields import ReCaptchaField


User = get_user_model()


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["username"].widget.input_type = "email"  # ugly hack
        self.fields["username"].label = ""
        self.fields["password"].label = ""

        self.helper.layout = Layout(
            Field("username", label="", placeholder=_("Enter Email"), autofocus=""),
            HTML('<div class="m-4"></div>'),
            Field("password", placeholder=_("Enter Password")),
            HTML(
                '<div class="mt-3 mb-4">Forgot Password? <a href="{}" class="pt-1 mb-5">Remember me</a></div>'.format(
                    reverse("accounts:password-reset")
                )
            ),
            StrictButton(_("Log in"), css_class="btn btn-secondary", type="Submit")

        )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                try:
                    user_temp = User.objects.get(email=username)
                except User.DoesNotExist:
                    user_temp = None

                if user_temp is not None:
                    if not user_temp.is_active:
                        raise forms.ValidationError(
                            _("We see that your email address is in our database, but that you have not yet"
                              "confirmed your address. Please search for the confirmation email in your inbox"
                              "(or spam) to activate your account")
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
    surname = forms.CharField(
        required=True,
        max_length=20,
        label=_(""),
        widget=forms.TextInput(attrs={"placeholder": _("Enter Surname")})
    )
    profileVisible = forms.BooleanField(
        required=False,
        initial=False,
        label=_("Make profile visible to others"),
    )

    """
    username and phone are hidden Honeypot-Fields to prevent bots from submitting the form.
    """
    username = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={"style": "display:none;"}), 
    label=""
    )

    phone = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={"style": "display:none;"}), 
    label=""
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["email"].widget.input_type = "email"  # ugly hack
        self.fields["email"].label = ""
        self.fields["name"].label = ""
        self.fields["name"].widget.attrs.update({
            "maxlength": "20",  # Limit name to 20 characters
            "placeholder": _("Enter Name (max 20 characters)"),
        })
        self.fields["password1"].label = ""
        self.fields["password2"].label = ""
        self.fields["captcha"] = ReCaptchaField()
        self.fields["captcha"].label = ""
        self.helper.layout = Layout(
            Field("email", placeholder=_("Enter Email"), autofocus=""),
            HTML('<div class="m-4"></div>'),
            Field("name", placeholder=_("Enter Name (max 20 characters)"),),
            HTML('<div class="m-4"></div>'),
            Field("surname", placeholder=_("Enter Surname (max 20 characters)"),),
            Field("username", placeholder=_("Enter Username"),),
            Field("phone", placeholder=_("Enter Mobile Number"),),
            HTML('<div class="m-4"></div>'),
            Field("password1", placeholder=_("Enter Password")),
            HTML('<div class="m-4"></div>'),
            Field("password2", placeholder=_("Re-enter Password")),
            HTML('<div class="m-4"></div>'),
            Field("profileVisible"),
            HTML('<div class="m-4"></div>'),
            Field("captcha"),
            StrictButton(_("Sign up"), css_class="btn btn-secondary mt-5", type="Submit"),
        )
    
    def clean(self):
        cleaned_data = super().clean()

        # If honeypot fields are filled, reject the form
        if cleaned_data.get("username"):
            raise forms.ValidationError(_("Wrong username. Try Again."))
        elif cleaned_data.get("phone"):
            raise forms.ValidationError(_("Incorrecct phone number"))

        return cleaned_data

    def clean_name(self):
        name = self.cleaned_data.get("name")

        # Validate length
        if len(name) > 20:
            raise forms.ValidationError(_("Name must not exceed 20 characters."))

        # Validate contains no URLs
        if "http" in name.lower():
            raise forms.ValidationError(_("Name cannot contain the string 'http'."))

        # Validate prohibited words
        forbidden_words = ["bitcoin", "casino", "baby", "dear"]
        for word in forbidden_words:
            if word in name.lower():
                raise forms.ValidationError(_(f"Name cannot contain the word '{word}'."))

        return name

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Validate prohibited words
        forbidden_words = ["bitcoin", "casino", "baby", "dear"]
        for word in forbidden_words:
            if word in email.lower():
                raise forms.ValidationError(_(f"Email cannot contain the word '{word}'."))

        # Validate email dot count before @
        local_part = email.split('@')[0]
        if local_part.count('.') > 2:
            raise forms.ValidationError(_("Email cannot contain more than two dots before the '@'."))

        return email

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


class PasswordVerificationForm(forms.Form):
    """
    Verifying user's password for their account deletion.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": _("Password"), "autofocus": True}),
        label=_("Password"),
        required=True,
    )

    def __init__(self, *args, ** kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("password"),
            StrictButton(_("Delete Account"), css_class="btn-danger mt-3", type="Submit"),
        )
