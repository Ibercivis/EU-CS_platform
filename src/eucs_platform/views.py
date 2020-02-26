from django.views import generic
from django.shortcuts import render
from projects.models import Project
from resources.models import Resource, ResourceGroup, ResourcesGrouped, FeaturedResources
from blog.models import Post
from projects.models import FeaturedProjects, Project
import random
from django.shortcuts import get_object_or_404

def home(request):
    #groups = ResourceGroup.objects.get_queryset().order_by('id')
    #resourcesgrouped = ResourcesGrouped.objects.get_queryset().order_by('group')
    lastBlogEntry = Post.objects.all().filter(status=1)
    if lastBlogEntry:
        lastBlogEntry = lastBlogEntry.latest('created_on')
    featuredProjects = FeaturedProjects.objects.all()
    featuredProject = None
    if featuredProjects:
        featuredProject = random.choice(featuredProjects)
        featuredProject = get_object_or_404(Project, id=featuredProject.project_id)
    featuredResources = FeaturedResources.objects.all()
    featuredResource = None
    if featuredResources:
        featuredResource = random.choice(featuredResources)
        featuredResource = get_object_or_404(Resource, id=featuredResource.resource_id)
    
    return render(request, 'home.html', {'featuredProject':featuredProject, 'featuredResource':featuredResource, 'lastBlogEntry': lastBlogEntry})

class AboutPage(generic.TemplateView):
    template_name = "about.html"

class EventsPage(generic.TemplateView):
    template_name = "events.html"


def results(request):
    projects = Project.objects.get_queryset().order_by('id')
    resources = Resource.objects.get_queryset().order_by('id')
    showProjects = showResources = False

    if request.GET.get('keywords'):
        projects = projects.filter(name__icontains = request.GET['keywords'])
        resources = resources.filter(name__icontains = request.GET['keywords'])
    

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













