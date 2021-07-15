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
from django.http import HttpResponse

from ecsa.models import Ecsa_fee, InvoiceCounter
from ecsa.views import getEcsaInvoiceCounter
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from datetime import date

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = Profile
    fieldsets = (
    (None, {
        'fields':('lastname','picture','title', 'bio','interestAreas','latitude','longitude', 'orcid','organisation', 'occupation'),
    }),
    ('Address', {
        'fields': ('postal_code', 'city', 'country'),
    }),
    ('Ecsa address', {
        'fields': ('ecsa_street','ecsa_postal_code', 'ecsa_city', 'ecsa_country'),
    }),
    ('ECSA membership', {
        #'classes': ('collapse',),
        'fields': ('ecsa_requested_join','ecsa_reduced_fee','ecsa_old_member_fee','paid','ecsa_member_since','ecsa_community_mailing_list','ecsa_member_number','admin_send_welcome_email'),
    }),
    )
    readonly_fields = ('admin_send_welcome_email', )



class NewUserAdmin(NamedUserAdmin):
    inlines = [UserProfileInline]
    list_display = (
        "is_active",
        "email",
        "name",
        "permalink",
        "is_superuser",
        "is_staff",
    )
    list_filter = ["is_active", "profile__paid", "profile__ecsa_requested_join", "is_superuser"]

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
            paid = user_old.profile.paid
            mailingListOld = user_old.profile.ecsa_community_mailing_list
            ecsa_member_number = user_old.profile.ecsa_member_number
            year = date.today().year
            fee_id = 3
            discount_ecsa_old_member_fee = 0
            discount_ecsa_reduced_fee = 0
            ecsa_old_member_fee = 0
            ecsa_reduced_fee = 0
            try:
                base_amount = Ecsa_fee.objects.get(id=fee_id).amount
            except Ecsa_fee.DoesNotExist:
                base_amount = 200
            total_amount = base_amount
            
            if(obj.profile.ecsa_reduced_fee):
                try:
                    discount_ecsa_reduced_fee = Ecsa_fee.objects.get(id=4).amount
                    ecsa_reduced_fee = int(total_amount * discount_ecsa_reduced_fee / 100)
                    total_amount = total_amount - ecsa_reduced_fee
                except Ecsa_fee.DoesNotExist:
                    print("Ecsa fee discount not exist")

            if(obj.profile.ecsa_old_member_fee):
                try:
                    discount_ecsa_old_member_fee = Ecsa_fee.objects.get(id=5).amount
                    ecsa_old_member_fee = int(total_amount * discount_ecsa_old_member_fee / 100)
                    total_amount = total_amount - ecsa_old_member_fee
                except Ecsa_fee.DoesNotExist:
                    print("Ecsa fee discount not exist")

            if(obj.profile.ecsa_member_number and ecsa_member_number != obj.profile.ecsa_member_number):
                to_email = obj.email                
                subject = 'Welcome to ECSA!'
                message = render_to_string('accounts/emails/ecsa_member_accepted.html', { 'name': obj.name, 'lastname': obj.profile.lastname,
                 'ecsa_member_number': obj.profile.ecsa_member_number})
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"

                #PDF Attachment                        
                current_date = date.today()
                invoiceCounter = getEcsaInvoiceCounter()
                pdf_content =  render_to_string('accounts/pdf/ecsa_member_accepted.html', { 'ecsa_member_number': obj.profile.ecsa_member_number,
                 'year': year, 'current_date': current_date , 'name': obj.name, 'lastname': obj.profile.lastname, 'street': obj.profile.ecsa_street, 
                 'postal_code': obj.profile.ecsa_postal_code, 'city': obj.profile.ecsa_city, 'country': obj.profile.ecsa_country, 'ecsa_billing_email': obj.email,
                 'reduced_fee': obj.profile.ecsa_reduced_fee, 'ecsa_old_member_fee': obj.profile.ecsa_old_member_fee, 'amount': total_amount, 'invoiceCounter': str(invoiceCounter).zfill(4),
                 'base_amount': base_amount, 'discount_ecsa_old_member_fee': discount_ecsa_old_member_fee, 'ecsa_old_member_fee': ecsa_old_member_fee,
                 'discount_ecsa_reduced_fee': discount_ecsa_reduced_fee, 'ecsa_reduced_fee': ecsa_reduced_fee })
                filename = '/tmp/membership contribution'+ ' ' + str(obj.profile.ecsa_member_number) + '_' + str(year) + str(invoiceCounter).zfill(4) +'.pdf'
                HTML(string=pdf_content, base_url=request.build_absolute_uri()).write_pdf(filename)                
                email.attach_file(filename)
                
                email.send()
            if(not paid and paid != obj.profile.paid):
                to_email = obj.email
                subject = 'ECSA membership: Confirmation of payment and member badge'
                message = render_to_string('accounts/emails/ecsa_payment_confirmation.html', { 'name': obj.name, 'lastname': obj.profile.lastname, 'year': year,'total_amount': total_amount})
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"
                email.attach_file('static/site/img/ecsa_main_Member.jpg')
                email.send()
            
            #send email to add email in Ecsa mailing list
            if(obj.profile.paid and obj.profile.ecsa_community_mailing_list and 
                    ((paid != obj.profile.paid) or (mailingListOld !=obj.profile.ecsa_community_mailing_list) )):
                to_email = "vval@bifi.es" #ecsa-all-request@listserv.dfn.de
                subject = 'Add ECSA member to the community mailing list'
                message = "" + obj.email
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"
                email.send()
            #send email to delete email in Ecsa mailing list
            if(paid and mailingListOld and 
                    ((paid != obj.profile.paid) or (mailingListOld !=obj.profile.ecsa_community_mailing_list) )):
                obj.profile.ecsa_community_mailing_list = False
                to_email = "vval@bifi.es" #ecsa-all-request@listserv.dfn.de
                subject = 'Remove ECSA member from the community mailing list'
                message = "" + obj.email
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"
                email.send()
        
        user = super(NewUserAdmin, self).save_model(request, obj, form, change)




admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
