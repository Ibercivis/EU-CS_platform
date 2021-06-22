from django.contrib import admin
from .models import Organisation, OrganisationType
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from datetime import date
from ecsa.models import Ecsa_fee, InvoiceCounter
from ecsa.views import getEcsaInvoiceCounter

class OrganisationAdmin(admin.ModelAdmin):
    ordering = ('-name',)
    list_display = (
        "name",
        "orgType",
        "country",
        "paid",
    )
    list_filter = ["orgType", "paid", "ecsa_requested_join"]

    fieldsets = (
    (None, {
        'fields':('creator','name','origin_name','url', 'description','orgType','logo','contactPoint', 'contactPointEmail'),
    }),
    ('Address', {
        'fields': ('street','postal_code', 'city', 'latitude','longitude', 'country'),
    }),
    ('ECSA membership', {
        #'classes': ('collapse',),
        'fields': ('ecsa_requested_join','ecsa_billing_email', 'ecsa_billing_street', 'ecsa_billing_postal_code',
        'ecsa_billing_city', 'ecsa_billing_country', 'ecsa_reduced_fee','ecsa_old_organisation_fee','legal_status', 'vat_number',
        'paid','ecsa_member_since','ecsa_member_number','admin_send_welcome_email', 'mainDelegate', 'delegate1', 'delegate2'),
    }),
    )
    readonly_fields = ('admin_send_welcome_email', )

    def save_model(self, request, obj, form, change):        
        if change:
            id = obj.id
            organisation_old = get_object_or_404(Organisation, id=id)
            requested_join = organisation_old.ecsa_requested_join
            paid = organisation_old.paid
            ecsa_member_number = organisation_old.ecsa_member_number
            if(obj.ecsa_member_number and ecsa_member_number != obj.ecsa_member_number):
                to_email = obj.ecsa_billing_email                
                subject = 'Welcome to ECSA!'
                message = render_to_string('accounts/emails/ecsa_member_accepted.html', { 'name': obj.name,
                    'ecsa_member_number': obj.ecsa_member_number})
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"
                
                #PDF Attachment
                fee_id = (1, 2)[obj.legal_status == 1]
                discount_ecsa_old_member_fee = 0
                discount_ecsa_reduced_fee = 0
                ecsa_old_member_fee = 0
                ecsa_reduced_fee = 0
                try:
                    base_amount = Ecsa_fee.objects.get(id=fee_id).amount
                except Ecsa_fee.DoesNotExist:
                    base_amount = 200
                total_amount = base_amount


                if(obj.ecsa_reduced_fee):
                    try:
                        discount_ecsa_reduced_fee = Ecsa_fee.objects.get(id=4).amount
                        ecsa_reduced_fee = int(total_amount * discount_ecsa_reduced_fee / 100)
                        total_amount = total_amount - ecsa_reduced_fee
                    except Ecsa_fee.DoesNotExist:
                        print("Ecsa fee discount not exist")

                if(obj.ecsa_old_organisation_fee):
                    try:
                        discount_ecsa_old_member_fee = Ecsa_fee.objects.get(id=5).amount
                        ecsa_old_member_fee = int(total_amount * discount_ecsa_old_member_fee / 100)
                        total_amount = total_amount - ecsa_old_member_fee
                    except Ecsa_fee.DoesNotExist:
                        print("Ecsa fee discount not exist")

                
                year = date.today().year
                current_date = date.today()
                invoiceCounter = getEcsaInvoiceCounter()
                pdf_content =  render_to_string('accounts/pdf/ecsa_member_accepted.html', { 'ecsa_member_number': obj.ecsa_member_number,
                 'year': year, 'current_date': current_date , 'name': obj.name, 'street': obj.street, 'postal_code': obj.postal_code, 
                 'city': obj.city, 'country': obj.country, 'ecsa_billing_email': obj.ecsa_billing_email, 'reduced_fee': obj.ecsa_reduced_fee,
                 'ecsa_old_member_fee': obj.ecsa_old_organisation_fee, 'vat_number': obj.vat_number, 'legal_status': obj.legal_status, 'amount': total_amount, 'invoiceCounter': invoiceCounter,
                 'base_amount': base_amount, 'discount_ecsa_old_member_fee': discount_ecsa_old_member_fee, 'ecsa_old_member_fee': ecsa_old_member_fee,
                 'discount_ecsa_reduced_fee': discount_ecsa_reduced_fee, 'ecsa_reduced_fee': ecsa_reduced_fee })                         
                filename = '/tmp/membership_contribution'+ str(obj.ecsa_member_number) + '_' + str(year) + str(invoiceCounter) +'.pdf'
                HTML(string=pdf_content, base_url=request.build_absolute_uri()).write_pdf(filename)                
                email.attach_file(filename)
                

                email.send()
            if(not paid and paid != obj.paid):
                to_email = obj.ecsa_billing_email
                subject = 'Confirmation of payment'
                message = render_to_string('accounts/emails/ecsa_payment_confirmation.html', { 'name': obj.name})
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"
                email.send() 
        
        organisation = super(OrganisationAdmin, self).save_model(request, obj, form, change)

    
admin.site.register(OrganisationType)
admin.site.register(Organisation, OrganisationAdmin)