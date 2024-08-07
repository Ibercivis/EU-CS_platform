from django.contrib import admin
from django.db import models
from django.http.request import HttpRequest
from django.utils.html import format_html
from django_ckeditor_5.fields import CKEditor5Widget
from modeltranslation.admin import TabbedTranslationAdmin
from PIL import Image

# Register your models here.

from .models import Footer, HomeSection, Main, TopBar

# A new class to store the top bar
class HomeSectionAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'title', 'content_position', 'image_position')
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }
    pass

class MainAdmin(TabbedTranslationAdmin):
    list_display = ('platform_name', 'icon_tag')
    readonly_fields = ('icon_tag',)

    def icon_tag(self, obj):
        return format_html('<img src="{}" width="30" height="30" />'.format(obj.icon.url))
    
    icon_tag.short_description = 'Icon'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.icon.path)

        if img.height > 30 or img.width > 30:
            output_size = (30, 30)
            img.thumbnail(output_size)
            img.save(self.icon.path)

    def has_add_permission(self, request):
        return not Main.objects.exists()
    pass  

class TopBarAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'slug', 'position', 'parent', 'is_parent')
    ordering = ["-position"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(TopBarAdmin, self).get_form(request, obj, **kwargs)
        if obj and not obj.get_children().exists():
            form.base_fields['slug'].required = True
        else:
            form.base_fields['slug'].required = False
        return form

    def is_parent(self, obj):
        return obj.parent is None and obj.get_children().exists()

class FooterAdmin(TabbedTranslationAdmin):
    list_display = ('description',)
    def has_add_permission(self, request):
        return not Footer.objects.exists()
    pass
admin.site.register(Footer, FooterAdmin)
admin.site.register(Main, MainAdmin)
admin.site.register(HomeSection, HomeSectionAdmin)
admin.site.register(TopBar, TopBarAdmin)

