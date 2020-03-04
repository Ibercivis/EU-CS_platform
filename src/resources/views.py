from django.shortcuts import render
from .models import Resource, Keyword, Category, FeaturedResources, SavedResources
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .forms import ResourceForm
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from itertools import chain
from django.contrib.auth import get_user_model

User = get_user_model()

def resources(request):
    resources = Resource.objects.all()
    featuredResources = FeaturedResources.objects.all().values_list('resource_id',flat=True)

    savedResources = None
    user = request.user

    savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id',flat=True)

    languagesWithContent = Resource.objects.all().values_list('inLanguage',flat=True).distinct()

    filters = {'keywords': '', 'language': ''}
    
    if request.GET.get('keywords'):
        resources = resources.filter( Q(name__icontains = request.GET['keywords'])  | 
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
                                    
        filters['keywords'] = request.GET['keywords']

    if request.GET.get('language'):
        resources = resources.filter(inLanguage = request.GET['language'])
        filters['language'] = request.GET['language']

    if request.GET.get('license'):
        resources = resources.filter(license__icontains = request.GET['license'])
        filters['license'] = request.GET['license']

    return render(request, 'resources.html', {'resources':resources, 'featuredResources': featuredResources,
    'savedResources': savedResources, 'filters': filters, 'settings': settings, 'languagesWithContent': languagesWithContent})

def clearFilters(request):
    return redirect ('resources')

def new_resource(request):
    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)
    form = ResourceForm(initial={'choices': choices})
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

    if user != resource.creator and not user.is_staff:
        return redirect('../resources', {})

    keywordsList = list(resource.keywords.all().values_list('keyword', flat=True))
    keywordsList = ", ".join(keywordsList)

    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)

    form = ResourceForm(initial={
        'name':resource.name, 'abstract': resource.abstract, 'imageURL': resource.imageURL,
        'url': resource.url,'license': resource.license, 'choices': choices, 'theme': resource.theme,
        'audience' : resource.audience, 'publisher': resource.publisher, 'year_of_publication': resource.datePublished,
        'author': resource.author_rsc, 'author_email': resource.author_email, 'resource_DOI': resource.resourceDOI,
        'choicesSelected':keywordsList, 'category': getCategory(resource.category), 'categorySelected': resource.category.id
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

def resources_autocomplete(request):  
    if request.GET.get('q'):
        text = request.GET['q']
        rsc_names = Resource.objects.filter(name__icontains=text).values_list('name',flat=True).distinct()
        keywords = Keyword.objects.filter(keyword__icontains=text).values_list('keyword',flat=True).distinct()
        report = chain(rsc_names, keywords)
        json = list(report)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")

def license_autocomplete(request):  
    if request.GET.get('q'):
        text = request.GET['q']
        licenses = Resource.objects.filter(license__icontains=text).values_list('license',flat=True).distinct()
        json = list(licenses)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")

def get_sub_category(request):
    category = request.GET.get("category")
    options = '<select id="id_subcategory" class="select form-control">'
    response = {}

    if category:
        sub_categories = Category.objects.filter(parent=category)
        sub_categories = sub_categories.values_list("id","text")
        tupla_sub_categories = tuple(sub_categories)

        if tupla_sub_categories:
            for sub_category in tupla_sub_categories:
                options += '<option value = "%s">%s</option>' % (
                    sub_category[0],
                    sub_category[1]     
                )
            options += '</select>'
            response['sub_categories'] = options        
        else:
            response['sub_categories'] = '<select id="id_subcategory" class="select form-control" disabled></select>'
    else:
        response['sub_categories'] = '<select id="id_subcategory" class="select form-control" disabled></select>'
    return JsonResponse(response)


def getCategory(category):    
    if category.parent:
            return category.parent
    else:
        return category

def setFeaturedRsc(request):
    response = {}
    id = request.POST.get("resource_id")    

    #Delete
    try:
        obj = FeaturedResources.objects.get(resource_id=id)    
        obj.delete()
    except FeaturedResources.DoesNotExist:
        #Insert
        fResource = get_object_or_404(Resource, id=id)
        featureResource = FeaturedResources(resource=fResource)
        featureResource.save()

    return JsonResponse(response, safe=False) 

def setSavedResource(request):
    response = {}
    resourceId = request.POST.get("resource_id")
    userId = request.POST.get("user_id")

    #Delete
    try:
        obj = SavedResources.objects.get(resource_id=resourceId,user_id=userId)    
        obj.delete()
    except SavedResources.DoesNotExist:
        #Insert
        fResource = get_object_or_404(Resource, id=resourceId)
        fUser = get_object_or_404(User, id=userId)
        savedResource = SavedResources(resource=fResource, user=fUser)
        savedResource.save()

    return JsonResponse(response, safe=False) 