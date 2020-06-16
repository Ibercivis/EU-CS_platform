from django.views import generic
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from itertools import chain
from projects.models import Project,ApprovedProjects
from projects.views import getNamesKeywords
from resources.views import getRscNamesKeywords
from resources.models import Resource, ResourceGroup, ResourcesGrouped, ApprovedResources
from blog.models import Post
import random
import json


def home(request):
    approvedProjects = ApprovedProjects.objects.all().order_by('-id')[:3].values_list('project_id',flat=True)
    allapprovedProjects = ApprovedProjects.objects.all().order_by('-id').values_list('project_id',flat=True)
    projects = Project.objects.all().order_by('-id')
    allprojects =  projects.filter(id__in=allapprovedProjects)
    projects = projects.filter(id__in=approvedProjects)
    featuredProjects = Project.objects.all().filter(featured=True)[:3]
    featuredResources = Resource.objects.all().filter(featured=True)[:3]
    entries = Post.objects.filter(status=1).order_by('-created_on')[:3]
    approvedResources = ApprovedResources.objects.all().order_by('-id')[:3].values_list('resource_id',flat=True)
    resources = Resource.objects.all().order_by('-id')
    resources = resources.filter(id__in=approvedResources)
    return render(request, 'home.html', {'projects':projects, 'allprojects': allprojects, 'featuredProjects': featuredProjects, 'resources':resources, 'featuredResources': featuredResources, 'entries': entries}, )

class AboutPage(generic.TemplateView):
    template_name = "about.html"

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
