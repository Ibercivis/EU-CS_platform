from django.db import models
from django.conf import settings
from django_countries.fields import CountryField
from django.utils.translation import ugettext_lazy as _


LEGAL_STATUS = (
    (0,"Profit"),
    (1,"Non-profit")
)
"""
 YES_NO = (
    (0,"No"),
    (1,"Yes")
) 
"""

class OrganisationType(models.Model):
    type = models.TextField()
    def __str__(self):
        return f'{self.type}'

class Organisation(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='creator')
    dateCreated = models.DateTimeField('Created date', auto_now=True)
    dateUpdated = models.DateTimeField('Updated date', auto_now=True)
    
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    description = models.CharField(max_length=3000)
    orgType = models.ForeignKey(OrganisationType, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    contactPoint = models.CharField(max_length=100, null=True, blank=True)
    contactPointEmail = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9,decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9,decimal_places=6, null=True, blank=True)
    country = CountryField(null=True, blank=True)

    #Ecsa fields
    ecsa_member = models.BooleanField(null=True, blank=True)
    ecsa_requested_join = models.BooleanField(null=True, blank=True)
    ecsa_member_since = models.DateTimeField(null=True,blank=True)
    ecsa_payment_revision = models.BooleanField(null=True, blank=True)
    street = models.CharField(_("Street"), max_length=50, blank=True, null=True)
    postal_code = models.IntegerField(null=True, blank=True)
    city = models.CharField(_("City"), max_length=50, blank=True, null=True)    
    ecsa_billing_street = models.CharField(_("Street"), max_length=50, blank=True, null=True)
    ecsa_billing_postal_code = models.IntegerField(null=True, blank=True)
    ecsa_billing_city = models.CharField(_("City"), max_length=50, blank=True, null=True)
    ecsa_billing_country = models.CharField(_("Country"), max_length=50, blank=True, null=True)
    ecsa_billing_email = models.EmailField(blank=True, null=True)
    #occupation = models.ForeignKey(OrganisationType, null=True, blank=True, on_delete=models.CASCADE)
    legal_status = models.IntegerField(choices=LEGAL_STATUS)
    has_vat_number = models.BooleanField(default=False)
    vat_number = models.IntegerField(null=True, blank=True)
    ecsa_reduced_fee = models.BooleanField(_("Reduced fee"), default=False)
    ecsa_old_organisation_fee = models.BooleanField(_("Old organisation fee"), default=False)

    

    def __str__(self):
        return f'{self.name}'


class OrganisationPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)