from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.shortcuts import render
from django.core.mail import send_mail
from profiles.models import Profile
from authtools import views as authviews
from braces import views as bracesviews
from templated_mail.mail import BaseEmailMessage
from djoser import utils
from django.contrib.auth.tokens import default_token_generator
from .tokens import account_activation_token
from . import forms
from ecsa.models import Delegate, Ecsa_fee

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
        super().form_valid(form)
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        ecsa_individual_membership = form.cleaned_data.get('ecsa_individual_membership')
        mail_subject = 'Confirm your EU-Citizen.Science account'
        message = render_to_string('accounts/acc_active_email.html', {
            'user': user,
            'domain': settings.HOST,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        html_message = render_to_string('accounts/acc_active_email.html', {
            'user': user,
            'domain': settings.HOST,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })

        to_email = form.cleaned_data.get('email')
        send_mail(mail_subject, message, 'eu-citizen.science@ibercivis.es',[to_email], html_message=html_message)

        forms.saveProfile(form, user.id, ecsa_individual_membership)
        if(ecsa_individual_membership):
            newEcsaIndividualMembershipEmail(to_email, user.name, form.cleaned_data.get('lastname'))

        return render(self.request, 'accounts/confirm-email.html',{})

@login_required(login_url='/login')
def newEcsaIndividualMembership(request):
    form = forms.NewEcsaIndividualMembershipForm()
    try:
        individual_contribution = Ecsa_fee.objects.get(id=3).amount
    except Ecsa_fee.DoesNotExist:
        individual_contribution = 50
    if request.method == 'POST':
        form = forms.NewEcsaIndividualMembershipForm(request.POST)
        if form.is_valid():
            newEcsaIndividualMembershipEmail(request.user.email, request.user.name, request.user.profile.lastname)
            form.save(request, request.user.id)

        return redirect("profiles:show_self")

    return render(request, 'accounts/new_ecsa_individual_membership.html', {'form': form, 'individual_contribution': individual_contribution})

def newEcsaIndividualMembershipEmail(email, name, surname):
    to_email = email
    subject = 'Thank you! - Become a member of ECSA'
    message = render_to_string('accounts/emails/new_ecsa_individual_membership.html', { 'name': name, 'surname': surname})
    email = EmailMessage(subject, message, to=[to_email], bcc=settings.EMAIL_ECSA_ADMIN)
    email.content_subtype = "html"
    email.send()

@login_required(login_url='/login')
def editEcsaIndividualMembership(request):
    user = get_object_or_404(User, id=request.user.id)
    form = forms.NewEcsaIndividualMembershipForm(initial={
        'ecsa_reduced_fee': user.profile.ecsa_reduced_fee, 'ecsa_old_member_fee': user.profile.ecsa_old_member_fee,
        'street': user.profile.street, 'postal_code': user.profile.postal_code, 'city': user.profile.city, 'country' : user.profile.country, 'occupation' : user.profile.occupation
    })
    try:
        individual_contribution = Ecsa_fee.objects.get(id=3).amount
    except Ecsa_fee.DoesNotExist:
        individual_contribution = 50
  

    if request.method == 'POST':
        form = forms.NewEcsaIndividualMembershipForm(request.POST, request.FILES)     
        if form.is_valid():
            form.save(request, request.user.id)
            return redirect('profiles:show_self')
        else:
            print(form.errors)
    return render(request, 'accounts/editEcsaIndividualMembership.html', {'form': form, 'user':user, 'individual_contribution': individual_contribution})


def dropOutECSAmembership(request):
    profile = get_object_or_404(Profile, user_id=request.user.id)    
    profile.ecsa_requested_join = False
    profile.ecsa_member = False
    profile.save()
    return redirect("profiles:show_self")

def claimEcsaPaymentRevision(request):
    profile = get_object_or_404(Profile, user_id=request.user.id)  
    profile.ecsa_payment_revision = True
    profile.save()
    #send email
    subject = 'ECSA membership payment revision'
    from_email = request.user.email
    message = "I want an ECSA membership payment revision"
    try:
        send_mail(subject, message, from_email, settings.EMAIL_CONTACT_RECIPIENT_LIST, html_message=message)
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
    return redirect("profiles:show_self")

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
    extra_email_context = { 'PASSWORD_RESET_TIMEOUT_HOURS': settings.PASSWORD_RESET_TIMEOUT_DAYS * 24,
                            'domain': settings.HOST }

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
        mail_subject = 'Welcome to EU-Citizen.Science!'
        message = render_to_string('accounts/welcome_email.html', {
            'user': user,
            "domain": settings.HOST,
        })
        to_email = user.email
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.content_subtype = "html"
        email.send()

        #Set delegates with this email
        try:
            delegate = get_object_or_404(Delegate, email=user.email)
            delegate.user = user
            delegate.save()
        except Delegate.DoesNotExist:
            print("There isn't delegate")

        auth.login(request, user)
        return render(request, 'accounts/confirmation-account.html',{})
    else:
        return HttpResponse('Activation link is invalid!')


class PasswordResetEmail(BaseEmailMessage):
    template_name = "accounts/emails/password-reset-email.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["domain"] = settings.HOST
        context["url"] = settings.PASSWORD_RESET_CONFIRM_URL.format(**context)
        return context

class ActivationEmail(BaseEmailMessage):
    template_name = "accounts/acc_active_email.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = account_activation_token.make_token(user)
        context["url"] = settings.ACTIVATION_URL.format(**context)
        context["domain"] = settings.HOST
        return context


class ConfirmationEmail(BaseEmailMessage):
    template_name = "accounts/welcome_email.html"