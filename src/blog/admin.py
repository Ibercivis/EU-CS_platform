from django.contrib import admin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django_summernote.widgets import SummernoteWidget
from django import forms
from .models import Post

def make_published(modeladmin, request, queryset):
    queryset.update(status=1)
make_published.short_description = "Mark selected posts as published"

def make_draft(modeladmin, request, queryset):
    queryset.update(status=0)
make_draft.short_description = "Mark selected posts as draft"

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
                ['misc', ['link', 'picture', 'video', 'undo', 'redo', 'help', ]],
            ],

        })
        return summernote_settings


class CustomPostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {'content': SummernoteModelAdminWithCustomToolbar()}
        fields = "__all__"


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'sticky', 'excerpt', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    form = CustomPostForm
    actions = [make_published, make_draft]
    change_form_template = "blog_change_form.html"

    def response_change(self, request, obj):
        if "_preview" in request.POST:
            form = CustomPostForm(request.POST)
            if form.data['title'] and form.data['excerpt'] and form.data['content']:
                post = get_object_or_404(Post, slug=form.data['slug'])
                objectA = post
                return render(request, "preview_post_detail.html", { 'object':objectA, 'post':post})
            else:
                print(form.errors)

        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if "_preview" in request.POST:
            form = CustomPostForm(request.POST)
            if form.data['title'] and form.data['excerpt'] and form.data['content']:
                post = get_object_or_404(Post, slug=form.data['slug'])
                objectA = post
                return render(request, "preview_post_detail.html", { 'object':objectA, 'post':post})
            else:
                print(form.errors)

        return super().response_add(request, obj, post_url_continue=None)

admin.site.register(Post, PostAdmin)
