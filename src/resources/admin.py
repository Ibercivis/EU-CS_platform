from django.contrib import admin
from .models import Resource, ResourceGroup, ResourcesGrouped
# Register your models here.

admin.site.register(Resource)
admin.site.register(ResourceGroup)
admin.site.register(ResourcesGrouped)
