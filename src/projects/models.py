from django.db import models
from django.conf import settings


class Project(models.Model):
    name = models.CharField(max_length=100)
    category =  models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    start_date = models.DateTimeField('Start date')
    end_date = models.DateTimeField('End date')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):        
        return f'{self.name}'

class Category(models.Model):
    category = models.TextField()
    def __str__(self):        
        return f'{self.category}'