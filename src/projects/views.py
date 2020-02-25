from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from .forms import ProjectForm
from django.utils import timezone
from .models import Project, Topic, Status, Keyword, Votes
from django.contrib.auth import get_user_model
import json
from django.utils.dateparse import parse_datetime
from datetime import datetime
from django.utils import formats
from django.contrib import messages
from PIL import Image
from django.db.models import Q
from itertools import chain
from django.db.models import Avg, Max, Min, Sum


def new_project(request):
    form = ProjectForm()
    user = request.user
    if request.method == 'POST':    
        form = ProjectForm(request.POST, request.FILES)
       
        if form.is_valid():            
            filepath = request.FILES.get('image', False)
            image_path = ''
            if (filepath):
                x = form.cleaned_data.get('x')
                y = form.cleaned_data.get('y')
                w = form.cleaned_data.get('width')
                h = form.cleaned_data.get('height')
                photo = request.FILES['image']
                image = Image.open(photo)
                cropped_image = image.crop((x, y, w+x, h+y))
                resized_image = cropped_image.resize((400, 300), Image.ANTIALIAS)
                _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
                image_path = "media/images/" + _datetime + '_' + photo.name 
                resized_image.save(image_path)   

            form.save(request, '/' + image_path)

            messages.success(request, "Project added with success!")
            return redirect('/projects')
        else:
            print(form.errors)

    return render(request, 'new_project.html', {'form': form, 'user':user})

def projects(request):
    projects = Project.objects.get_queryset().order_by('id')

    topics = Topic.objects.all()
    status = Status.objects.all()
    filters = {'keywords': '', 'topic': '', 'status': 0, 'country': '', 'host': ''}

    if request.GET.get('keywords'):
        projects = projects.filter( Q(name__icontains = request.GET['keywords']) | 
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
        filters['keywords'] = request.GET['keywords']    
    
    if request.GET.get('topic'):
        projects = projects.filter(topic__topic = request.GET['topic'])
        filters['topic'] = request.GET['topic']

    if request.GET.get('status'):
        projects = projects.filter(status = request.GET['status'])
        filters['status'] = int(request.GET['status'])

    if request.GET.get('country'):
        projects = projects.filter(country = request.GET['country'])
        filters['country'] = request.GET['country']
    
    if request.GET.get('host'):
        projects = projects.filter( host__icontains = request.GET['host'])
        filters['host'] = request.GET['host']  

    paginator = Paginator(projects, 9) 
    page = request.GET.get('page')
    projects = paginator.get_page(page)

    return render(request, 'projects.html', {'projects': projects, 'topics': topics,
    'status': status, 'filters': filters})


def project(request, pk):
    project = get_object_or_404(Project, id=pk)
    votes = Votes.objects.all().filter(project_id=pk).aggregate(Avg('vote'))['vote__avg']
    print(votes)
    return render(request, 'project.html', {'project':project,'votes':votes})

def editProject(request, pk):
    project = get_object_or_404(Project, id=pk)
    user = request.user    
    if user != project.creator and not user.is_staff:
        return redirect('../projects', {})
    
    start_datetime = formats.date_format(project.start_date, 'Y-m-d')
    end_datetime = formats.date_format(project.end_date, 'Y-m-d')    
  
    keywordsList = list(project.keywords.all().values_list('keyword', flat=True))
    keywordsList = ", ".join(keywordsList)
    choices = keywordsList
    form = ProjectForm(initial={
        'project_name':project.name,'url': project.url,'start_date': start_datetime,
        'end_date':end_datetime, 'aim': project.aim, 'description': project.description, 
        'choices': choices, 'status': project.status, 
        'topic':project.topic.all, 'latitude': project.latitude, 'longitude': project.longitude, 
        'image': project.image, 'image_credit': project.imageCredit, 'host': project.host,
        'how_to_participate': project.howToParticipate, 'equipment': project.equipment,
    })
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            filepath = request.FILES.get('image', False)
            image_path = ''
            if (filepath):
                x = form.cleaned_data.get('x')
                y = form.cleaned_data.get('y')
                w = form.cleaned_data.get('width')
                h = form.cleaned_data.get('height')
                photo = request.FILES['image']
                image = Image.open(photo)
                cropped_image = image.crop((x, y, w+x, h+y))
                resized_image = cropped_image.resize((400, 300), Image.ANTIALIAS)
                _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
                image_path = "media/images/" + _datetime + '_' + photo.name 
                resized_image.save(image_path)   

            form.save(request, '/' + image_path)
            return redirect('/project/'+ str(pk))
        else:
            print(form.errors)
    return render(request, 'editProject.html', {'form': form, 'project':project, 'user':user})


def deleteProject(request, pk):
    obj = get_object_or_404(Project, id=pk)
    obj.delete()        
    return redirect('projects')

def text_autocomplete(request):  
    if request.GET.get('q'):
        text = request.GET['q']
        project_names = Project.objects.filter(name__icontains=text).values_list('name',flat=True).distinct()
        keywords = Keyword.objects.filter(keyword__icontains=text).values_list('keyword',flat=True).distinct()
        report = chain(project_names, keywords)
        json = list(report)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")


def host_autocomplete(request):  
    if request.GET.get('q'):
        text = request.GET['q']
        data = Project.objects.filter(host__icontains=text).values_list('host',flat=True)               
        json = list(data)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")

def clearFilters(request):
    return redirect ('projects')
