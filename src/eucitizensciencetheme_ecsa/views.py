from django.views import generic
from datetime import datetime
from django.shortcuts import render
from django.template.response import TemplateResponse
from .models import HomeSection, Main
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q

from projects.models import Project, Likes, Follows
from resources.models import Resource
from organisations.models import Organisation
from platforms.models import Platform
from profiles.models import Profile
from events.models import Event
from django.shortcuts import get_object_or_404

# Create your views here, in alphabetical order

def about(request):
    return TemplateResponse(request, 'about.html', {})

def call(request):
    return TemplateResponse(request, 'call.html', {})

def call_ambassadors(request):
    return TemplateResponse(request, 'call_ambassadors.html', {})

def criteria(request):
    return TemplateResponse(request, 'criteria.html',{})

def development(request):
    return TemplateResponse(request, 'development.html',{})

def ecs_project(request):
    return TemplateResponse(request, 'ecs_project.html',{})

def ecs_project_ambassadors(request):
    return TemplateResponse(request, 'ecs_project_ambassadors.html',{})

def ecs_project_codesign(request):
    return TemplateResponse(request, 'ecs_project_codesign.html',{})

def faq(request):
    return TemplateResponse(request, 'faq.html',{})

def final_event(request):
    return TemplateResponse(request, 'final_event.html',{})

def final_launch(request):
    return TemplateResponse(request, 'final_launch.html',{})

def get_projects(request):
    # Filter approved projects with non-null mainOrganisation
    projects = Project.objects.filter(approved=True).prefetch_related('projectCountry')

    markers = []
    for project in projects:
        # Check if the project has projectCountry related
        if project.projectCountry.exists():
            for country in project.projectCountry.all():
                marker = {
                    'latitude': country.latitude,
                    'longitude': country.longitude,
                    'name': project.name,
                    'project_url': f'/project/{project.id}',
                    'project_id': project.id
                }
                markers.append(marker)
        elif project.mainOrganisation:
            # Use mainOrganisation if there's no projectCountry
            marker = {
                'latitude': project.mainOrganisation.latitude,
                'longitude': project.mainOrganisation.longitude,
                'name': project.name,
                'project_url': f'/project/{project.id}',
                'project_id': project.id
            }
            markers.append(marker)
        # Not add marker if there is no projectCountry and mainOrganisation

    return JsonResponse({'markers': markers})

def get_organisations(request):
    # Filter approved projects with non-null mainOrganisation
    organisations = Organisation.objects.filter(approved=True)

    # Create a list of marker dictionaries with the required data
    markers = []
    for organisation in organisations:
        marker = {
            'latitude': organisation.latitude,
            'longitude': organisation.longitude,
            'name': organisation.name,
            'organisation_url': f'/organisation/{organisation.id}',
        }
        markers.append(marker)

    # Return marker data in JSON format
    return JsonResponse({'markers': markers})

def home(request):
    # Projects
    user = request.user
    main = get_object_or_404(Main)
    projects = Project.objects.get_queryset().filter(~Q(hidden=True)).filter(approved=True).order_by('-dateCreated')
    projectsCounter = len(projects)
    paginatorprojects = Paginator(projects, 3)
    page = request.GET.get('page')
    projects = paginatorprojects.get_page(page)
    # To only show some topics and keywords
    for project in projects:
        combined = list(project.topic.all()) + list(project.keywords.all())
        if len(combined) > 3:
            project.display_items = combined[:3]
            project.more_count = len(combined) - 3
        else:
            project.display_items = combined
            project.more_count = 0
            
    if user.is_authenticated:
        likes = Likes.objects.filter(user=request.user)
        likes = likes.values_list('project', flat=True)
        follows = Follows.objects.filter(user=request.user)
        follows = follows.values_list('project', flat=True)
    else:
        likes = None
        follows = None

    # Resources
    resources = Resource.objects.all().filter(~Q(isTrainingResource=True)).filter(approved=True).order_by('-dateCreated')
    resources = resources.filter(approved=True)
    resourcesCounter = len(resources)
    paginatorresources = Paginator(resources, 4)
    page = request.GET.get('page')
    resources = paginatorresources.get_page(page)

    # Training Resources
    trainingResources = Resource.objects.all().filter(isTrainingResource=True).filter(approved=True).order_by('-dateCreated')
    trainingResourcesCounter = len(trainingResources)
    paginatorTrainingResources = Paginator(trainingResources, 4)
    page = request.GET.get('page')
    trainingResources = paginatorTrainingResources.get_page(page)

    # Organisations
    organisations = Organisation.objects.all().filter(approved=True).order_by('-dateCreated')
    organisationsCounter = len(organisations)
    paginatororganisation = Paginator(organisations, 4)
    page = request.GET.get('page')
    organisations = paginatororganisation.get_page(page)

    # Platforms
    platforms = Platform.objects.all().filter(approved=True).order_by('-dateCreated')
    platformsCounter = len(platforms)
    paginatorPlatform = Paginator(platforms, 4)
    page = request.GET.get('page')
    platforms = paginatorPlatform.get_page(page)

    # Events
    now = datetime.today()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    events = Event.objects.all().filter(start_date__gt=now).order_by('-featured', 'start_date')
    paginatorEvents = Paginator(events, 3)
    page = request.GET.get('page')
    events = paginatorEvents.get_page(page)

    # Users
    # TODO: Filter users by active
    usersCounter = Profile.objects.filter().count()

    sections = HomeSection.objects.all()

    return TemplateResponse(request, 'home.html', {
        'user': user,
        'main': main,
        'projects': projects,
        'likes': likes,
        'follows': follows,
        'projectsCounter': projectsCounter,
        'resources': resources,
        'resourcesCounter': resourcesCounter,
        'trainingResourcesCounter': trainingResourcesCounter,
        'organisations': organisations,
        'organisationsCounter': organisationsCounter,
        'platforms': platforms,
        'platformsCounter': platformsCounter,
        'usersCounter': usersCounter,
        'events': events,
        'sections': sections,
        'isSearchPage': True})

def imprint(request):
    return TemplateResponse(request, 'pages/imprint.html', {})

def moderation(request):
    return TemplateResponse(request, 'pages/moderation.html', {})

def moderation_quality_criteria(request):
    return TemplateResponse(request, 'pages/moderation_quality_criteria.html', {})

def policy_brief(request):
    return TemplateResponse(request, 'pages/policy_brief.html', {})

def policy_maker_event_2021(request):
    return TemplateResponse(request, 'pages/policy_maker_event_2021.html', {})

def privacy(request):
    return TemplateResponse(request, 'pages/privacy.html', {})

def projects_map(request):
    return TemplateResponse(request, 'pages/map.html', {})

def subscribe(request):
    return TemplateResponse(request, 'pages/subscribe.html', {})

def terms(request):
    return TemplateResponse(request, 'pages/terms.html', {})

def test(request):
    return TemplateResponse(request, 'base_r2.html', {})

def test2(request):
    return TemplateResponse(request, 'base_r2old.html', {})

def translations(request):
    return TemplateResponse(request, 'pages/translations.html', {})





