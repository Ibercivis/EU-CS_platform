from django.db import models

# Create your models here.

# A new class to store the top bar
class TopBar(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    position = models.IntegerField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        verbose_name_plural = "TopBar"
        ordering = ["position"]

    def __str__(self):
        return self.name
    
# Only one footer is allowed
class Footer(models.Model):
    description = models.TextField()
    link_name1 = models.CharField(max_length=200, blank = True)
    link_url1 = models.CharField(max_length=200, blank= True)
    link_name2 = models.CharField(max_length=200, blank = True)
    link_url2 = models.CharField(max_length=200, blank= True)
    link_name3 = models.CharField(max_length=200, blank = True)
    link_url3 = models.CharField(max_length=200, blank= True)
    link_name4 = models.CharField(max_length=200, blank = True)
    link_url4 = models.CharField(max_length=200, blank= True)
    link_name5 = models.CharField(max_length=200, blank=True)
    link_url5 = models.CharField(max_length=200, blank=True)
    link_name6 = models.CharField(max_length=200, blank=True)
    link_url6 = models.CharField(max_length=200, blank=True)
    link_name7 = models.CharField(max_length=200, blank=True)
    link_url7 = models.CharField(max_length=200, blank=True)
    link_name8 = models.CharField(max_length=200, blank=True)
    link_url8 = models.CharField(max_length=200, blank=True)

    license = models.CharField(max_length=200, blank=True)
    license_url = models.CharField(max_length=200, blank=True)

    
    facebook_url = models.CharField(max_length=200, blank=True)
    twitter_url = models.CharField(max_length=200, blank=True)
    instagram_url = models.CharField(max_length=200, blank=True)

    def clean(self):
        if Footer.objects.count() > 1:
            raise ValidationError('Only one footer is allowed')
    def save(self, *args, **kwargs):
        self.clean()
        super(Footer, self).save(*args, **kwargs)
    
    def __str__(self):
        return "footer"
    
class HomeSection(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()
    position = models.IntegerField()
    image = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)

    # order by position
    class Meta:
        verbose_name_plural = "HomeSection"
        ordering = ["position"]

    def __str__(self):
        return self.name

