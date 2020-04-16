from django.views import generic
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from itertools import chain
from projects.models import Project,FeaturedProjects
from projects.views import getNamesKeywords
from resources.views import getRscNamesKeywords
from resources.models import Resource, ResourceGroup, ResourcesGrouped, FeaturedResources
from blog.models import Post
import random
import json


def home(request):
    #groups = ResourceGroup.objects.get_queryset().order_by('id')
    #resourcesgrouped = ResourcesGrouped.objects.get_queryset().order_by('group')
    try:
        featuredProjectsFixed = [59,54]
        featuredProjects = []
        featuredProjectFixed1 = FeaturedProjects.objects.get(project_id=featuredProjectsFixed[0]).project_id
        featuredProjects.append(featuredProjectFixed1)
        featuredProjectFixed2 = FeaturedProjects.objects.get(project_id=featuredProjectsFixed[1]).project_id
        featuredProjects.append(featuredProjectFixed2)
        featuredProject3 = FeaturedProjects.objects.exclude(project_id__in=featuredProjectsFixed)
        if(featuredProject3):
            featuredProject3 = featuredProject3.last().project_id
            featuredProjects.append(featuredProject3)
    except FeaturedProjects.DoesNotExist:
        featuredProjects = FeaturedProjects.objects.all().order_by('-id')[:3].values_list('project_id',flat=True)

    allfeaturedProjects = FeaturedProjects.objects.all().order_by('-id').values_list('project_id',flat=True)
    projects = Project.objects.all().order_by('-id')
    allprojects =  projects.filter(id__in=allfeaturedProjects)
    projects = projects.filter(id__in=featuredProjects)
    entries = Post.objects.filter(status=1).order_by('-created_on')[:3]
    featuredResources = FeaturedResources.objects.all().order_by('-id')[:3].values_list('resource_id',flat=True)
    resources = Resource.objects.all().order_by('-id')
    resources = resources.filter(id__in=featuredResources)
    return render(request, 'home.html', {'projects':projects, 'allprojects': allprojects,'resources':resources, 'entries': entries}, )

class AboutPage(generic.TemplateView):
    template_name = "about.html"


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

def faq(request):
    return render(request, 'faq.html')

def development(request):
    return render(request, 'development.html')

def subscribe(request):
    return render(request, 'subscribe.html')

def moderation(request):
    return render(request, 'moderation.html')
def criteria(request):
    return render(request, 'criteria.html')


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
