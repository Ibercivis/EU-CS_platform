from django.contrib import admin
from .models import Organisation, OrganisationType


class OrganisationAdmin(admin.ModelAdmin):
    list_filter = ('orgType',)
    ordering = ('-name',)


admin.site.register(OrganisationType)
admin.site.register(Organisation, OrganisationAdmin)
