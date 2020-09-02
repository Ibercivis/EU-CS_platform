from django.views import generic
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
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
    #Projects
    user = request.user
    projects = Project.objects.get_queryset().filter(~Q(hidden=True)).order_by('featured','id')
    approvedProjects = ApprovedProjects.objects.all().values_list('project_id',flat=True)
    followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id',flat=True)

    filters = {'keywords': ''}

    if request.GET.get('keywords'):
        projects = projects.filter( Q(name__icontains = request.GET['keywords']) |
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
        filters['keywords'] = request.GET['keywords']
    counterprojects = len(projects)
    paginatorprojects = Paginator(projects, 4)
    page = request.GET.get('page')
    projects = paginatorprojects.get_page(page)




    #Resources
    resources = Resource.objects.get_queryset().filter(~Q(isTrainingResource=True)).filter(~Q(hidden=True)).order_by('featured','id')
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
    counterresources = len(resources)
    paginatorresources = Paginator(resources, 8)
    page = request.GET.get('page')
    resources = paginatorresources.get_page(page)


    #Training Resources
    tresources = Resource.objects.get_queryset().filter(isTrainingResource=True).order_by('id')
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
    countertresources = len(tresources)
    paginatortresources = Paginator(tresources, 8)
    page = request.GET.get('page')
    tresources = paginatortresources.get_page(page)

    organisations = Organisation.objects.all().order_by('-id')

    return render(request, 'home.html', {'projects':projects, 'counterprojects':counterprojects, \
        'resources':resources, 'counterresources':counterresources,\
        'filters': filters, \
        'tresources':tresources, 'countertresources':countertresources,
        'organisations': organisations})

def all(request):
    return home(request)

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
