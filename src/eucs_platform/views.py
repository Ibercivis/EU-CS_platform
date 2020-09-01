from django.views import generic
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from itertools import chain
from projects.models import Project,ApprovedProjects, FollowedProjects
from projects.views import getNamesKeywords
from resources.views import getRscNamesKeywords
from resources.models import Resource, ResourceGroup, ResourcesGrouped, ApprovedResources, SavedResources, Theme, Category
from organisations.models import Organisation
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

def home_r2(request):
    #Projects
    projects = Project.objects.get_queryset()
    approvedProjects = ApprovedProjects.objects.all().values_list('project_id',flat=True)
    user = request.user
    followedProjects = None
    followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id',flat=True)
    countriesWithContent = Project.objects.all().values_list('country',flat=True).distinct()
    filters = {'keywords': ''}

    if request.GET.get('keywords'):
        projects = projects.filter( Q(name__icontains = request.GET['keywords']) |
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
        filters['keywords'] = request.GET['keywords']

    projects = projects.filter(~Q(hidden=True))
    projectsTop = projects.filter(featured=True)
    projectsTopIds = list(projectsTop.values_list('id',flat=True))
    projects = projects.exclude(id__in=projectsTopIds)
    # Pin projects to top
    projects = list(projectsTop) + list(projects)


    #Resources
    resources = Resource.objects.all().filter(~Q(isTrainingResource=True)).order_by('id')

    approvedResources = ApprovedResources.objects.all().values_list('resource_id',flat=True)
    savedResources = None
    savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id',flat=True)
    languagesWithContent = Resource.objects.all().values_list('inLanguage',flat=True).distinct()
    themes = Theme.objects.all()
    categories = Category.objects.all()
    if request.GET.get('keywords'):
        resources = resources.filter( Q(name__icontains = request.GET['keywords'])  |
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
        filters['keywords'] = request.GET['keywords']

    resources = resources.filter(~Q(hidden=True))
    resourcesTop = resources.filter(featured=True)
    resourcesTopIds = list(resourcesTop.values_list('id',flat=True))
    resources = resources.exclude(id__in=resourcesTopIds)
    resources = list(resourcesTop) + list(resources)

    #Training Resources
    tresources = Resource.objects.all().filter(isTrainingResource=True).order_by('id')
    tapprovedResources = ApprovedResources.objects.all().values_list('resource_id',flat=True)
    tsavedResources = None
    tsavedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id',flat=True)
    if request.GET.get('keywords'):
        tresources = tresources.filter( Q(name__icontains = request.GET['keywords'])  |
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
        filters['keywords'] = request.GET['keywords']

    tresources = tresources.filter(~Q(hidden=True))
    tresourcesTop = tresources.filter(featured=True)
    tresourcesTopIds = list(tresourcesTop.values_list('id',flat=True))
    tresources = tresources.exclude(id__in=tresourcesTopIds)
    tresources = list(tresourcesTop) + list(tresources)

    organisations = Organisation.objects.all().order_by('-id')

    return render(request, 'home_r2.html', {'projects':projects, 'resources':resources, 'tresources':tresources, 'organisations': organisations})

def all(request):
    approvedProjects = ApprovedProjects.objects.all().order_by('-id')[:6].values_list('project_id',flat=True)
    projects = Project.objects.all().order_by('-id')
    projects = projects.filter(id__in=approvedProjects)
    approvedResources = ApprovedResources.objects.all().order_by('-id')[:6].values_list('resource_id',flat=True)
    resources = Resource.objects.all().order_by('-id')
    resources = resources.filter(id__in=approvedResources).filter(~Q(isTrainingResource=True))
    trainingResources = Resource.objects.all().filter(isTrainingResource=True).order_by('id')[:6]
    organisations = Organisation.objects.all().order_by('-id')[:6]
    return None

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
