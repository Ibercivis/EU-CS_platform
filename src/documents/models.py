from django.db import models

# Create your models here.
class Document(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.CharField(max_length=300)
    datePublished = models.DateTimeField('Date Published')
    #document = models.FileField(upload_to='documents/')

    def __str__(self):
        return self.name