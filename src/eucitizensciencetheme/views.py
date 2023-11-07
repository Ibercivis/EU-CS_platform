from django.views import generic
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import JsonResponse

from projects.models import Project

# Create your views here, in alphabetical order

def about(request):
    return TemplateResponse(request, 'about.html', {})

def all(request):
    return TemplateResponse(request, 'home.html', {})

def call(request):
    return TemplateResponse(request, 'call.html', {})

def call_ambassadors(request):
    return TemplateResponse(request, 'call_ambassadors.html', {})

def criteria(request):
    return TemplateResponse(request, 'criteria.html',{})

def development(request):
    return TemplateResponse(request, 'development.html',{})

def ecs_project_ambassadors(request):
    return TemplateResponse(request, 'ecs_project_ambassadors.html',{})

def faq(request):
    return TemplateResponse(request, 'faq.html',{})

def final_event(request):
    return TemplateResponse(request, 'final_event.html',{})

def final_launch(request):
    return TemplateResponse(request, 'final_launch.html',{})

def get_markers(request):
    # Filter approved projects with non-null mainOrganisation
    projects = Project.objects.filter(approved=True, mainOrganisation__isnull=False)

    # Create a list of marker dictionaries with the required data
    markers = []
    for project in projects:
        marker = {
            'latitude': project.mainOrganisation.latitude,
            'longitude': project.mainOrganisation.longitude,
            'name': project.name,
            'project_url': f'/project/{project.id}',
        }
        markers.append(marker)

    # Return marker data in JSON format
    return JsonResponse({'markers': markers})

def imprint(request):
    return TemplateResponse(request, 'imprint.html', {})

def moderation(request):
    return TemplateResponse(request, 'moderation.html', {})

def moderation_quality_criteria(request):
    return TemplateResponse(request, 'moderation_quality_criteria.html', {})

def policy_brief(request):
    return TemplateResponse(request, 'policy_brief.html', {})

def policy_maker_event_2021(request):
    return TemplateResponse(request, 'policy_maker_event_2021.html', {})

def privacy(request):
    return TemplateResponse(request, 'privacy.html', {})

def projects_map(request):
    return TemplateResponse(request, 'projects_map.html', {})

def subscribe(request):
    return TemplateResponse(request, 'subscribe.html', {})

def terms(request):
    return TemplateResponse(request, 'terms.html', {})

def translations(request):
    return TemplateResponse(request, 'translations.html', {})





