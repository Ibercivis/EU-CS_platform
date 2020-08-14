from django.db import models
from django.conf import settings

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
    logo = models.ImageField(upload_to='images/', max_length=300)
    contactPoint = models.CharField(max_length=100, null=True, blank=True)
    contactPointEmail = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=150)
  

    def __str__(self):
        return f'{self.name}'
