from django.contrib import admin
from .models import Resource, ResourceGroup, ResourcesGrouped
# Register your models here.

class ResourcesGroupedAdmin(admin.ModelAdmin):
    list_filter = ('group','resource',)
    ordering = ('-group',)

admin.site.register(Resource)
admin.site.register(ResourceGroup)
admin.site.register(ResourcesGrouped, ResourcesGroupedAdmin)
