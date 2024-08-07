from django.db import models

# Create your models here.


class Main(models.Model):
    icon = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    platform_name = models.CharField(max_length=200)
    platform_description = models.TextField()
    platform_url = models.URLField(max_length=200)


class TopBar(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, blank=True, null=True)
    position = models.IntegerField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = "TopBar"
        ordering = ["position"]

    def __str__(self):
        return self.name

    def get_children(self):
        return TopBar.objects.filter(parent=self).order_by('position')

    @property
    def is_parent(self):
        return self.parent is None and self.get_children().exists()
    
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
    # position is a selector con float-left, float-right
    content_position = models.CharField(
        max_length=15,
        choices=(("order-1", "left"), ("order-2", "right")))
    image = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    image_position = models.CharField(
        max_length=15,
        choices=(("order-1", "left"), ("order-2", "right")))

    # order by position
    class Meta:
        verbose_name_plural = "HomeSection"

    def __str__(self):
        return self.name

