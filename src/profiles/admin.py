from __future__ import unicode_literals
from django.contrib import admin
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from authtools.admin import NamedUserAdmin
from django.template.loader import render_to_string
from .models import Profile
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = Profile
    fieldsets = (
    (None, {
        'fields':('lastname','picture','title', 'bio','interestAreas','latitude','longitude', 'email_verified', 'orcid','organisation', 'occupation'),
    }),
    ('Address', {
        'fields': ('street','postal_code', 'city', 'country'),
    }),
    ('ECSA membership', {
        #'classes': ('collapse',),
        'fields': ('ecsa_requested_join','ecsa_payment_revision','ecsa_billing_email','ecsa_reduced_fee','ecsa_old_member_fee','ecsa_member','ecsa_member_since','ecsa_member_number','admin_send_welcome_email'),
    }),
    )
    readonly_fields = ('admin_send_welcome_email', )



class NewUserAdmin(NamedUserAdmin):
    change_form_template = "profiles/change_form_test.html"
    inlines = [UserProfileInline]
    list_display = (
        "is_active",
        "email",
        "name",
        "permalink",
        "is_superuser",
        "is_staff",
    )
    list_filter = ["is_active", "profile__ecsa_member", "profile__ecsa_requested_join", "is_superuser"]    

    # 'View on site' didn't work since the original User model needs to
    # have get_absolute_url defined. So showing on the list display
    # was a workaround.
    def permalink(self, obj):
        url = reverse("profiles:show", kwargs={"slug": obj.profile.slug})
        # Unicode hex b6 is the Pilcrow sign
        return format_html('<a href="{}">{}</a>'.format(url, "\xb6"))


    def save_model(self, request, obj, form, change):
        if change:
            id = obj.id
            user_old = get_object_or_404(User, id=id)
            requested_join = user_old.profile.ecsa_requested_join
            ecsa_member = user_old.profile.ecsa_member
            ecsa_member_number = user_old.profile.ecsa_member_number
            if(ecsa_member_number != obj.profile.ecsa_member_number):
                to_email = obj.email
                subject = 'Welcome to ECSA!'
                message = render_to_string('accounts/emails/ecsa_member_accepted.html', { 'name': obj.name,
                 'ecsa_member_number': obj.profile.ecsa_member_number})
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"
                #email.attach("tst","../../static/site/files/EU-Cit.Sci_Guide_for_Applicants.pdf")
                email.send()
            if(not ecsa_member and ecsa_member != obj.profile.ecsa_member):
                to_email = obj.email
                subject = 'Confirmation of payment'
                message = render_to_string('accounts/emails/ecsa_payment_confirmation.html', { 'name': obj.name})
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"
                email.send()
        


        user = super(NewUserAdmin, self).save_model(request, obj, form, change)




admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
