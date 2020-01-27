from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from .forms import ProjectForm
from django.utils import timezone
from .models import Project, Category, Status
from django.contrib.auth import get_user_model
import json
from django.utils.dateparse import parse_datetime
from datetime import datetime
from django.utils import formats
from django.contrib import messages


def new_project(request):
    form = ProjectForm()
    user = request.user
    if request.method == 'POST':
        form = ProjectForm(request.POST) 
        if form.is_valid():
            form.save(request)
            messages.success(request, "Project added with success!")
            return redirect('/projects')

    return render(request, 'new_project.html', {'form': form, 'user':user})

def projects(request):
    projects = Project.objects.get_queryset().order_by('id')

    categories = Category.objects.all()
    status = Status.objects.all()
    filters = {'keywords': '', 'category': 0, 'status': 0}
    

    if request.GET.get('keywords'):
        projects = projects.filter(name__icontains = request.GET['keywords'])
        filters['keywords'] = request.GET['keywords']
    
    if request.GET.get('category'):
        projects = projects.filter(topic__icontains = request.GET['category'])
        filters['category'] = int(request.GET['category'])

    if request.GET.get('status'):
        projects = projects.filter(status = request.GET['status'])
        filters['status'] = int(request.GET['status'])

    paginator = Paginator(projects, 8) 
    page = request.GET.get('page')
    projects = paginator.get_page(page)

    return render(request, 'projects.html', {'projects': projects, 'categories': categories,
    'status': status, 'filters': filters})


def project(request, pk):
    project = get_object_or_404(Project, id=pk)
    categories = selectCategories(project.topic)

    return render(request, 'project.html', {'project':project, 'categories': categories})

def editProject(request, pk):
    project = get_object_or_404(Project, id=pk)
    user = request.user
    if user != project.creator:
        return redirect('../projects', {})
    
    start_datetime = formats.date_format(project.start_date, 'Y-m-d')
    end_datetime = formats.date_format(project.end_date, 'Y-m-d')    
    categories = selectCategories(project.topic)

    form = ProjectForm(initial={
        'project_name':project.name,'url': project.url,'start_date': start_datetime,
        'end_date':end_datetime, 'aim': project.aim, 'description': project.description, 
        'keywords': project.keywords, 'status': project.status, 
        'topic':categories, 'latitude': project.latitude, 'longitude': project.longitude, 
        'image': project.image, 'image_credit': project.imageCredit, 'host': project.host,
        'how_to_participate': project.howToParticipate, 'equipment': project.equipment,
    })
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('/project/'+ str(pk))
    return render(request, 'editProject.html', {'form': form, 'project':project, 'user':user})

def selectCategories(projCategories):
    proj_categories = projCategories.split('#')
    categories = ''
    if proj_categories[0] != '':
        categories = Category.objects.filter(id__in=proj_categories)
    return categories

def deleteProject(request, pk):
    obj = get_object_or_404(Project, id=pk)
    obj.delete()        
    return redirect('projects')

def text_autocomplete(request):  
    if request.GET.get('q'):
        text = request.GET['q']
        data = Project.objects.filter(name__icontains=text).values_list('name',flat=True)
        json = list(data)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")

def clearFilters(request):
    return redirect ('projects')