from django.shortcuts import render
from .models import Pages
from django.template.response import TemplateResponse

# Create your views here.
def page(request, slug):
    page = Pages.objects.get(slug=slug)
    return TemplateResponse(request, 'page.html', {'page': page})
