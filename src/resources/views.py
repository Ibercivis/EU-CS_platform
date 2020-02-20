from django.shortcuts import render
from .models import Resource, Keyword
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .forms import ResourceForm
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.conf import settings
from django.db.models import Q


def resources(request):
    resources = Resource.objects.all()
    filters = {'keywords': ''}
    
    if request.GET.get('keywords'):
        resources = resources.filter( Q(name__icontains = request.GET['keywords'])  | 
                                    Q(keywords__keyword__icontains = request.GET['keywords']) )
                                    
        filters['keywords'] = request.GET['keywords']

    return render(request, 'resources.html', {'resources':resources, 'filters': filters})

def clearFilters(request):
    return redirect ('resources')

def new_resource(request):
    form = ResourceForm()
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)

        if form.is_valid():
            form.save(request)
            messages.success(request, "Resource uploaded with success!")
            return redirect('/resources')

    return render(request, 'new_resource.html', {'form': form, 'settings': settings})


def resource(request, pk):
    resource = get_object_or_404(Resource, id=pk)

    return render(request, 'resource.html', {'resource':resource})

def editResource(request, pk):
    resource = get_object_or_404(Resource, id=pk)
    user = request.user

    if user != resource.author:
        return redirect('../resources', {})

    keywordsList = list(resource.keywords.all().values_list('keyword', flat=True))
    keywordsList = ", ".join(keywordsList)
    choices = keywordsList

    form = ResourceForm(initial={
        'name':resource.name,'about': resource.about, 'abstract': resource.abstract, 
        'url': resource.url,'license': resource.license,
        'audience' : resource.audience, 'publisher': resource.publisher,
        'choices': choices  
    })
    
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('/resource/'+ str(pk))

    return render(request, 'editResource.html', {'form': form, 'resource': resource,
     'user': user, 'settings': settings })

def deleteResource(request, pk):
    obj = get_object_or_404(Resource, id=pk)
    obj.delete()        
    return redirect('resources')