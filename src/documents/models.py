from django.db import models
from django.conf import settings

class Document(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    about  = models.CharField(max_length=200)
    abstract = models.CharField(max_length=300)
    aggregateRating = models.CharField(max_length=100)
    audience = models.CharField(max_length=100)
    datePublished = models.DateTimeField('Date Published')
    inLanguage = models.CharField(max_length=100)
    keywords = models.CharField(max_length=100)
    license =  models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)

    def __str__(self):
        return self.name