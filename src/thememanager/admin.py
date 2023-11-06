from django.contrib import admin

# Register your models here.

from .models import TopBar

# A new class to store the top bar
class TopBarAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'position','parent')
    ordering = ["-position"]

admin.site.register(TopBar, TopBarAdmin)
