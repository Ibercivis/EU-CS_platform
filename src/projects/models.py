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

class FundingBody(models.Model):
    body = models.TextField()
    def __str__(self):
        return f'{self.body}'

class OriginDatabase(models.Model):
    originDatabase = models.TextField()
    def __str__(self):
        return f'{self.originDatabase}'

class CustomField(models.Model):
    title = models.TextField()
    paragraph = models.TextField()

class Project(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #Database information
    dateCreated = models.DateTimeField('Created date', auto_now=True)
    dateUpdated = models.DateTimeField('Updated date', auto_now=True)
    origin = models.CharField(max_length=100)
    #Basic Project Information
    name = models.CharField(max_length=200)
    aim = models.CharField(max_length=2000)
    description = models.CharField(max_length=3000)
    keywords = models.ManyToManyField(Keyword)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    start_date = models.DateTimeField('Start date',null=True, blank=True)
    end_date = models.DateTimeField('End date',null=True, blank=True)
    topic = models.ManyToManyField(Topic)
    url = models.CharField(max_length=200)
    #Contact person info
    author = models.CharField(max_length=100, null=True, blank=True)
    author_email =  models.CharField(max_length=100)
    #Images and communications
    image1 = models.ImageField(upload_to='images/', max_length=300)
    imageCredit1 = models.CharField(max_length=300, null=True, blank=True)
    image2 = models.ImageField(upload_to='images/', max_length=300,null=True, blank=True)
    imageCredit2 = models.CharField(max_length=300)
    image3 = models.ImageField(upload_to='images/', max_length=300,null=True, blank=True)
    imageCredit3 = models.CharField(max_length=300, null=True, blank=True)
    #Geography
    latitude = models.DecimalField(max_digits=9,decimal_places=6)
    longitude = models.DecimalField(max_digits=9,decimal_places=6)
    country = CountryField()
    #Personal and Organizational Affiliates
    host = models.CharField(max_length=200)
    #Supplementary information for Citizen Science
    howToParticipate = models.CharField(max_length=2000)
    doingAtHome      = models.BooleanField(null=True, default=False)
    equipment = models.CharField(max_length=2000)
    #Funding
    fundingBody = models.ForeignKey(FundingBody, on_delete=models.CASCADE,null=True, blank=True)
    fundingProgram = models.CharField(max_length=500)
    #Origin information
    originDatabase = models.ForeignKey(OriginDatabase, on_delete=models.CASCADE,null=True, blank=True)
    originURL = models.CharField(max_length=200)
    originUID = models.CharField(max_length=200)

    hidden = models.BooleanField(null=True, blank=True)

    customField = models.ManyToManyField(CustomField)
    def __str__(self):
        return f'{self.name}'


class FeaturedProjects(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.project}'


class FollowedProjects(models.Model):
    class Meta:
        unique_together = (('user', 'project'),)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.project} - {self.user.name}'

class ProjectPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
