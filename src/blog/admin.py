from django.contrib import admin
from django.templatetags.static import static
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django_summernote.widgets import SummernoteWidget
from django_summernote.admin import SummernoteModelAdmin
from django import forms
from .models import Post

def make_published(modeladmin, request, queryset):
    queryset.update(status=1)
make_published.short_description = "Mark selected posts as published"

def make_draft(modeladmin, request, queryset):
    queryset.update(status=0)
make_draft.short_description = "Mark selected posts as draft"

class CustomPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"


class PostAdmin(SummernoteModelAdmin):
    list_display = ('title', 'slug', 'status', 'sticky', 'excerpt', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    model = Post
    summernote_fields = ('content',)
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
