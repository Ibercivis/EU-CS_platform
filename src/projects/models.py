from django.db import models
from django.conf import settings
from django_countries.fields import CountryField


class Status(models.Model):
    status = models.TextField()
    def __str__(self):        
        return f'{self.status}'

class Topic(models.Model):
    topic = models.TextField()
    def __str__(self):        
        return f'{self.topic}'

class Keyword(models.Model):
    keyword = models.TextField()
    def __str__(self):        
        return f'{self.keyword}'

class Project(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #Database information
    dateCreated = models.DateTimeField('Created date', auto_now=True)
    dateUpdated = models.DateTimeField('Updated date', auto_now=True)
    origin = models.CharField(max_length=100)
    #Basic Project Information
    name = models.CharField(max_length=100)
    aim = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    keywords = models.ManyToManyField(Keyword)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    start_date = models.DateTimeField('Start date')
    end_date = models.DateTimeField('End date')
    topic = models.ManyToManyField(Topic)
    url = models.CharField(max_length=200)

    #Images and communications
    image = models.ImageField(upload_to='images/', max_length=300)
    imageCredit = models.CharField(max_length=200)
    #Geography
    latitude = models.DecimalField(max_digits=9,decimal_places=6)
    longitude = models.DecimalField(max_digits=9,decimal_places=6)
    country = CountryField()
    #Personal and Organizational Affiliates
    host = models.CharField(max_length=100)
    #Supplementary information for Citizen Science
    howToParticipate = models.CharField(max_length=300)
    equipment = models.CharField(max_length=200)
		#Rate
		#TODO: Do we want to use it?
    #rate = models.DecimalField(max_digits=2,decimal_places=1)
    #nvoters = models.IntegerField()
    def __str__(self):        
        return f'{self.name}'


class Votes(models.Model):
    vote = models.DecimalField(max_digits=2,decimal_places=1)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):        
        return f'{self.vote}'

class FeaturedProjects(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    def __str__(self):        
        return f'{self.project}'


class FollowedProjects(models.Model):
    class Meta:
        unique_together = (('user', 'project'),)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)