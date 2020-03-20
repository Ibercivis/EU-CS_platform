from django.contrib import admin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.urls import reverse
from django.conf import settings
from django_summernote.widgets import SummernoteWidget
from django import forms
from .models import Post


class SummernoteModelAdminWithCustomToolbar(SummernoteWidget):
    def summernote_settings(self):
        summernote_settings = settings.SUMMERNOTE_CONFIG.get(
            'summernote', {}).copy()
        lang = settings.SUMMERNOTE_CONFIG['summernote'].get('lang')
        if not lang:
            lang = 'en-US'
        summernote_settings.update({
            'width': '80%',
            'height': '500',
            'lang': lang,
            'url': {
                'language': static('summernote/lang/summernote-' + lang + '.min.js'),
                'upload_attachment': reverse('django_summernote-upload_attachment'),
            },
            'toolbar': [
                ['style', ['style', ]],
                ['font', ['bold', 'italic', 'underline', 'color', ]],
                ['paragraph', ['paragraph', 'ol', 'ul', ]],
                ['misc', ['link', 'picture', 'undo', 'redo', 'help', ]],
            ],

        })
        return summernote_settings


class CustomPostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {'content': SummernoteModelAdminWithCustomToolbar()}
        fields = "__all__"


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    form = CustomPostForm


admin.site.register(Post, PostAdmin)
