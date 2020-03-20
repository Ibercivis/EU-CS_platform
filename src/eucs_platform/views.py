from django.views import generic
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from projects.models import Project
from resources.models import Resource, ResourceGroup, ResourcesGrouped, FeaturedResources
from blog.models import Post
from projects.models import FeaturedProjects, Project
import random
import json
from itertools import chain
from django.shortcuts import get_object_or_404
from django.db.models import Q
from projects.views import getNamesKeywords
from resources.views import getRscNamesKeywords

def home(request):
    #groups = ResourceGroup.objects.get_queryset().order_by('id')
    #resourcesgrouped = ResourcesGrouped.objects.get_queryset().order_by('group')
    lastBlogEntry = Post.objects.all().filter(status=1)
    if lastBlogEntry:
        lastBlogEntry = lastBlogEntry.latest('created_on')
    featuredProjects = FeaturedProjects.objects.all()[:4].values_list('project_id',flat=True)
    projects = Project.objects.all().order_by('id')
    projects = projects.filter(id__in=featuredProjects)
    featuredResources = FeaturedResources.objects.all()[:3].values_list('resource_id',flat=True)
    resources = Resource.objects.all().order_by('id')
    resources = resources.filter(id__in=featuredProjects)

    return render(request, 'home.html', {'projects':projects, 'resources':resources, 'lastBlogEntry': lastBlogEntry})

class AboutPage(generic.TemplateView):
    template_name = "about.html"

class EventsPage(generic.TemplateView):
    template_name = "events.html"


def results(request):
    projects = Project.objects.get_queryset().order_by('id')
    resources = Resource.objects.get_queryset().order_by('id')
    showProjects = showResources = True

    if request.GET.get('keywords'):
        projects = projects.filter( Q(name__icontains = request.GET['keywords']) |
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
        resources = resources.filter( Q(name__icontains = request.GET['keywords'])  |
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()


    if request.GET.get('projects_check'):
        showProjects = True

    if request.GET.get('resources_check'):
        showResources = True

    return render(request, 'results.html', {'projects': projects, 'resources': resources,
    'showProjects': showProjects, 'showResources': showResources})

def curated(request):
    groups = ResourceGroup.objects.get_queryset().order_by('id')
    resourcesgrouped = ResourcesGrouped.objects.get_queryset().order_by('group')
    return render(request, 'curated.html', {'groups': groups, 'resourcesgrouped': resourcesgrouped})

def imprint(request):
    return render(request, 'imprint.html')

def contact(request):
    return render(request, 'contact.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')

def help(request):
    return render(request, 'help.html')

def status(request):
    return render(request, 'status.html')


def home_autocomplete(request):
    if request.GET.get('q'):
        text = request.GET['q']
        resources = getRscNamesKeywords(text)
        projects = getNamesKeywords(text)
        report = chain(resources, projects)
        json = list(report)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")
