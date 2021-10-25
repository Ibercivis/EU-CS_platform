from django.db import models
from django.conf import settings
from django.urls import reverse


STATUS = (
    (0, "Draft"),
    (1, "Publish")
)
STICKY = (
    (0, "No"),
    (1, "Yes")
)


class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=1000, default="")
    image = models.ImageField(max_length=200, default='default_blog.png')
    created_on = models.DateTimeField()
    sticky = models.IntegerField(choices=STICKY, default=0)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
                'post_detail', args=[
                    self.created_on.year,
                    self.created_on.strftime('%m'),
                    self.created_on.strftime('%d'),
                    self.slug])
