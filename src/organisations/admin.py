from django.contrib import admin
from .models import Organisation, OrganisationType
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from datetime import date
from ecsa.models import Ecsa_fee

class OrganisationAdmin(admin.ModelAdmin):
    ordering = ('-name',)
    list_display = (
        "name",
        "orgType",
        "country",
        "ecsa_member",
    )
    list_filter = ["orgType", "ecsa_member", "ecsa_requested_join"]

    fieldsets = (
    (None, {
        'fields':('creator','name','origin_name','url', 'description','orgType','logo','contactPoint', 'contactPointEmail'),
    }),
    ('Address', {
        'fields': ('street','postal_code', 'city', 'latitude','longitude', 'country'),
    }),
    ('ECSA membership', {
        #'classes': ('collapse',),
        'fields': ('ecsa_requested_join','ecsa_payment_revision','ecsa_billing_email', 'ecsa_billing_street', 'ecsa_billing_postal_code',
        'ecsa_billing_city', 'ecsa_billing_country', 'ecsa_reduced_fee','ecsa_old_organisation_fee','legal_status', 'vat_number',
        'ecsa_member','ecsa_member_since','ecsa_member_number','admin_send_welcome_email'),
    }),
    )
    readonly_fields = ('admin_send_welcome_email', )

    def save_model(self, request, obj, form, change):        
        if change:
            id = obj.id
            organisation_old = get_object_or_404(Organisation, id=id)
            requested_join = organisation_old.ecsa_requested_join
            ecsa_member = organisation_old.ecsa_member
            ecsa_member_number = organisation_old.ecsa_member_number
            if(ecsa_member_number != obj.ecsa_member_number):
               # to_email = obj.ecsa_billing_email
                to_email = "vval@bifi.es"
                subject = 'Welcome to ECSA!'
                message = render_to_string('accounts/emails/ecsa_member_accepted.html', { 'name': obj.name,
                    'ecsa_member_number': obj.ecsa_member_number})
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"
                
                #PDF Attachment
                fee_id = (1, 2)[obj.legal_status == 1]
                try:
                    fee_amount = Ecsa_fee.objects.get(id=fee_id).amount                
                except Ecsa_fee.DoesNotExist:
                    fee_amount = 200

                if(obj.ecsa_old_organisation_fee):
                    try:
                        discount = Ecsa_fee.objects.get(id=5).amount
                        fee_amount = fee_amount - int(fee_amount * discount / 100)
                    except Ecsa_fee.DoesNotExist:
                        print("Ecsa fee discount not exist")

                if(obj.ecsa_reduced_fee):
                    try:
                        discount = Ecsa_fee.objects.get(id=4).amount
                        fee_amount = fee_amount - int(fee_amount * discount / 100)
                    except Ecsa_fee.DoesNotExist:
                        print("Ecsa fee discount not exist")
                year = date.today().year
                current_date = date.today()
                pdf_content =  render_to_string('accounts/pdf/ecsa_member_accepted.html', { 'ecsa_member_number': obj.ecsa_member_number,
                 'year': year, 'current_date': current_date , 'name': obj.name, 'street': obj.street, 'postal_code': obj.postal_code, 
                 'city': obj.city, 'country': obj.country, 'ecsa_billing_email': obj.ecsa_billing_email, 'reduced_fee': obj.ecsa_reduced_fee,
                 'ecsa_old_member_fee': obj.ecsa_old_organisation_fee, 'vat_number': obj.vat_number, 'legal_status': obj.legal_status, 'amount':fee_amount })
                HTML(string=pdf_content, base_url=request.build_absolute_uri()).write_pdf('/tmp/membership_contribution.pdf')                
                email.attach_file('/tmp/membership_contribution.pdf')
                

                email.send()
            if(not ecsa_member and ecsa_member != obj.ecsa_member):
                to_email = obj.ecsa_billing_email
                subject = 'Confirmation of payment'
                message = render_to_string('accounts/emails/ecsa_payment_confirmation.html', { 'name': obj.name})
                email = EmailMessage(subject, message, to=[to_email], )
                email.content_subtype = "html"
                email.send() 
        
        organisation = super(OrganisationAdmin, self).save_model(request, obj, form, change)

    
admin.site.register(OrganisationType)
admin.site.register(Organisation, OrganisationAdmin)