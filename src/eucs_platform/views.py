from django.views import generic
from django.shortcuts import render
from projects.models import Project
from resources.models import Resource


class HomePage(generic.TemplateView):
    template_name = "home.html"


class AboutPage(generic.TemplateView):
    template_name = "about.html"


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