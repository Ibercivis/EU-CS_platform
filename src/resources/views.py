from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import formats
from itertools import chain
from authors.models import Author
from PIL import Image
from datetime import datetime
from .models import Resource, Keyword, Category, FeaturedResources, SavedResources, Theme, Category
from .forms import ResourceForm


User = get_user_model()

def resources(request):
    resources = Resource.objects.all().order_by('id')
    featuredResources = FeaturedResources.objects.all().values_list('resource_id',flat=True)
    user = request.user
    savedResources = None
    savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id',flat=True)
    languagesWithContent = Resource.objects.all().values_list('inLanguage',flat=True).distinct()
    themes = Theme.objects.all()
    categories = Category.objects.all()
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
    if request.GET.get('theme'):
        resources = resources.filter(theme = request.GET['theme'])
        filters['theme'] = int(request.GET['theme'])

    if request.GET.get('category'):
        resources = resources.filter(theme = request.GET['category'])
        filters['category'] = int(request.GET['category'])


    if request.GET.get('featuredCheck'):        
        resources = resources.filter(id__in=featuredResources)
        filters['featured'] = request.GET['featuredCheck']

     
    if not user.is_staff:
        resources = resources.filter(~Q(hidden=True)) 


    paginator = Paginator(resources, 8)
    page = request.GET.get('page')
    resources = paginator.get_page(page)

    return render(request, 'resources.html', {'resources':resources, 'featuredResources': featuredResources,
    'savedResources': savedResources, 'filters': filters, 'settings': settings, 'languagesWithContent': languagesWithContent, 'themes':themes, 'categories': categories})

def clearFilters(request):
    return redirect ('resources')

def new_resource(request):
    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)
    authorsCollection = list(Author.objects.all().values_list('author',flat=True))
    authorsCollection = ", ".join(authorsCollection)
    form = ResourceForm(initial={'choices': choices, 'authorsCollection': authorsCollection})
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
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
            messages.success(request, "Resource uploaded with success!")
            return redirect('/resources')

    return render(request, 'new_resource.html', {'form': form, 'settings': settings})


def resource(request, pk):
    resource = get_object_or_404(Resource, id=pk)
    user = request.user
    savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id',flat=True) #TODO: Only ask for the resource
    featuredResources = FeaturedResources.objects.all().values_list('resource_id',flat=True)
    return render(request, 'resource.html', {'resource':resource, 'savedResources':savedResources, 'featuredResources':featuredResources})

def editResource(request, pk):
    resource = get_object_or_404(Resource, id=pk)
    user = request.user

    if user != resource.creator and not user.is_staff:
        return redirect('../resources', {})

    keywordsList = list(resource.keywords.all().values_list('keyword', flat=True))
    keywordsList = ", ".join(keywordsList)
    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)
    selectedAuthors = list(resource.authors.all().values_list('author',flat=True))
    selectedAuthors = ", ".join(selectedAuthors)
    authorsCollection = list(Author.objects.all().values_list('author',flat=True))
    authorsCollection = ", ".join(authorsCollection)

    form = ResourceForm(initial={
        'name':resource.name, 'abstract': resource.abstract, 'image': resource.image,'resource_DOI': resource.resourceDOI,
        'url': resource.url,'license': resource.license, 'choices': choices, 'theme': resource.theme.all,
        'audience' : resource.audience, 'publisher': resource.publisher, 'year_of_publication': resource.datePublished,
        'authors': resource.authors.all, 'selectedAuthors': selectedAuthors, 'authorsCollection': authorsCollection,
        'author_email': resource.author_email, 'choicesSelected':keywordsList, 
        'category': getCategory(resource.category), 'categorySelected': resource.category.id
    })
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
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


def setHiddenResource(request):
    response = {}
    id = request.POST.get("resource_id")
    hidden = request.POST.get("hidden")
    resource = get_object_or_404(Resource, id=id)
    resource.hidden = False if hidden == 'false' else True
    resource.save()
    return JsonResponse(response, safe=False) 