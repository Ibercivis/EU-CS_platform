from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.shortcuts import render
from django.core.mail import send_mail
from authtools import views as authviews
from braces import views as bracesviews
from .tokens import account_activation_token
from . import forms


User = get_user_model()


class LoginView(bracesviews.AnonymousRequiredMixin, authviews.LoginView):
    template_name = "accounts/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        redirect = super().form_valid(form)
        remember_me = form.cleaned_data.get("remember_me")
        if remember_me is True:
            ONE_MONTH = 30 * 24 * 60 * 60
            expiry = getattr(settings, "KEEP_LOGGED_DURATION", ONE_MONTH)
            self.request.session.set_expiry(expiry)
        return redirect


class LogoutView(authviews.LogoutView):
    url = reverse_lazy("home")


class SignUpView(
    bracesviews.AnonymousRequiredMixin,
    bracesviews.FormValidMessageMixin,
    generic.CreateView,
):
    form_class = forms.SignupForm
    model = User
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("home")
    form_valid_message = "You're signed up!"

    def form_valid(self, form):
        r = super().form_valid(form)
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        mail_subject = 'Activate your EU-Citizen.Science account.'
        message = render_to_string('accounts/acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.send()
        #send_mail(mail_subject,message,"recover@ibercivis.es",[to_email])
        return render(self.request, 'accounts/confirm-email.html',{})


class PasswordChangeView(authviews.PasswordChangeView):
    form_class = forms.PasswordChangeForm
    template_name = "accounts/password-change.html"
    success_url = reverse_lazy("accounts:logout")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Your password was changed, "
            "hence you have been logged out. Please relogin",
        )

        return super().form_valid(form)


class PasswordResetView(authviews.PasswordResetView):
    form_class = forms.PasswordResetForm
    template_name = "accounts/password-reset.html"
    success_url = reverse_lazy("accounts:password-reset-done")
    subject_template_name = "accounts/emails/password-reset-subject.txt"
    email_template_name = "accounts/emails/password-reset-email.html"


class PasswordResetDoneView(authviews.PasswordResetDoneView):
    template_name = "accounts/password-reset-done.html"


class PasswordResetConfirmView(authviews.PasswordResetConfirmAndLoginView):
    template_name = "accounts/password-reset-confirm.html"
    form_class = forms.SetPasswordForm


def delete_user(request):
    try:
        u = User.objects.get(id = request.user.id)
        u.delete()
        messages.success(request, "The user has been deleted.")
    except User.DoesNotExist:
        messages.error = 'User does not exist.'
    except Exception as e:
        messages.error = 'There was a problem trying delete an user'

    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        #Send email
        mail_subject = 'Welcome to EU-Citizen.Science.'
        message = render_to_string('accounts/welcome_email.html', {
            'user': user,
        })
        to_email = user.email        
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.content_subtype = "html"
        email.send()
        auth.login(request, user)
        return render(request, 'accounts/confirmation-account.html',{})
    else:
        return HttpResponse('Activation link is invalid!')
