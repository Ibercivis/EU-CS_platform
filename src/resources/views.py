from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.db.models import Q, Avg
from django.contrib.auth import get_user_model
from django.utils import formats
from itertools import chain
from authors.models import Author
from PIL import Image
from datetime import datetime
from reviews.models import Review
from .models import Resource, Keyword, Category, ApprovedResources, SavedResources, Theme, Category, ResourcesGrouped,\
     ResourcePermission, EducationLevel, LearningResourceType, UnApprovedResources
from .forms import ResourceForm, ResourcePermissionForm
import csv
import random

User = get_user_model()

def training_resources(request):
    return resources(request, True)

def resources(request, isTrainingResource=False):
    if(isTrainingResource):
        resources = Resource.objects.all().filter(isTrainingResource=True).order_by('-dateLastModification')
    else:
        resources = Resource.objects.all().filter(~Q(isTrainingResource=True)).order_by('-dateLastModification')
    approvedResources = ApprovedResources.objects.all().values_list('resource_id',flat=True)
    unApprovedResources = UnApprovedResources.objects.all().values_list('resource_id',flat=True)
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

    resources = applyFilters(request, resources)
    filters = setFilters(request, filters)
    resources = resources.distinct()
    resources = resources.filter(~Q(hidden=True))


    if not user.is_staff:
        resources = resources.exclude(id__in=unApprovedResources)

    # Ordering
    if request.GET.get('orderby'):
        orderBy = request.GET.get('orderby')
        if("featured" in orderBy):
            resourcesTop = resources.filter(featured=True)
            resourcesTopIds = list(resourcesTop.values_list('id',flat=True))
            resources = resources.exclude(id__in=resourcesTopIds)
            resources = list(resourcesTop) + list(resources)
        elif("avg" in orderBy):
            reviews = Review.objects.filter(content_type=ContentType.objects.get(model="resource"))
            reviews = reviews.values("object_pk", "content_type").annotate(avg_rating=Avg('rating')).order_by(orderBy).values_list('object_pk',flat=True)
            reviews = list(reviews)
            resourcesVoted = []
            for r in reviews:
                rsc = Resource.objects.get(pk=r)
                if rsc in resources:
                    resourcesVoted.append(rsc)
            resources = resources.exclude(id__in=reviews)
            resources = list(resourcesVoted) + list(resources)
        else:
            resources=resources.order_by('-dateLastModification')
        filters['orderby']=request.GET['orderby']
    else:
        resources=resources.order_by('-dateLastModification')


    counter = len(resources)

    paginator = Paginator(resources, 12)
    page = request.GET.get('page')
    resources = paginator.get_page(page)

    return render(request, 'resources.html', {'resources':resources, 'approvedResources': approvedResources, 'unApprovedResources': unApprovedResources, 'counter': counter,
    'savedResources': savedResources, 'filters': filters, 'settings': settings, 'languagesWithContent': languagesWithContent,
    'themes':themes, 'categories': categories, 'isTrainingResource': isTrainingResource, 'isSearchPage': True})

@login_required(login_url='/login')
def new_training_resource(request):
    return new_resource(request, True)

@login_required(login_url='/login')
def new_resource(request, isTrainingResource=False):
    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)
    authorsCollection = list(Author.objects.all().values_list('author',flat=True))
    authorsCollection = ", ".join(authorsCollection)
    form = ResourceForm(initial={'choices': choices, 'authorsCollection': authorsCollection})
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            images = []
            image1_path = saveImage(request, form, 'image1','1')
            image2_path = saveImage(request, form, 'image2','2')
            images.append(image1_path)
            images.append(image2_path)
            form.save(request, images)
            if(isTrainingResource):
                return redirect('/training_resources')
            return redirect('/resources')

    return render(request, 'new_resource.html', {'form': form, 'settings': settings, 'isTrainingResource': isTrainingResource})

def training_resource(request, pk):
    return resource(request, pk)

def resource(request, pk):
    resource = get_object_or_404(Resource, id=pk)
    isTrainingResource = resource.isTrainingResource
    user = request.user
    users = getOtherUsers(resource.creator)
    cooperators = getCooperatorsEmail(pk)
    unApprovedResources = UnApprovedResources.objects.all().values_list('resource_id',flat=True)
    if (resource.id in unApprovedResources or resource.hidden) and ( user.is_anonymous or (user != resource.creator and not user.is_staff and not user.id in getCooperators(pk))):
        return redirect('../resources', {})
    permissionForm = ResourcePermissionForm(initial={'usersCollection':users, 'selectedUsers': cooperators})
    savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id',flat=True) #TODO: Only ask for the resource
    approvedResources = ApprovedResources.objects.all().values_list('resource_id',flat=True)
    return render(request, 'resource.html', {'resource':resource, 'savedResources':savedResources, 'approvedResources':approvedResources,
        'unApprovedResources': unApprovedResources, 'cooperators': getCooperators(pk), 'permissionForm': permissionForm, 'isTrainingResource': isTrainingResource,
        'isSearchPage': True})

def editTrainingResource(request, pk):
    return editResource(request, pk)

def editResource(request, pk):
    resource = get_object_or_404(Resource, id=pk)
    isTrainingResource  = resource.isTrainingResource
    user = request.user
    cooperators = getCooperators(pk)
    if user != resource.creator and not user.is_staff and not user.id in cooperators:
        if(isTrainingResource):
            return redirect('/training_resources')
        return redirect('../resources', {})

    users = getOtherUsers(resource.creator)
    cooperators = getCooperatorsEmail(pk)
    permissionForm = ResourcePermissionForm(initial={'usersCollection':users, 'selectedUsers': cooperators})

    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)

    authorsCollection = list(Author.objects.all().values_list('author',flat=True))
    authorsCollection = ", ".join(authorsCollection)

    curatedGroups = list(ResourcesGrouped.objects.all().filter(resource_id=pk).values_list('group_id', flat=True))

    educationLevel = list(EducationLevel.objects.all().values_list('educationLevel',flat=True))
    educationLevel = ", ".join(educationLevel)

    learningResourceType = list(LearningResourceType.objects.all().values_list('learningResourceType',flat=True))
    learningResourceType = ", ".join(learningResourceType)

    form = ResourceForm(initial={
        'name':resource.name, 'abstract': resource.abstract, 'image1': resource.image1, 'image2': resource.image2,'resource_DOI': resource.resourceDOI,
        'withImage1': (True, False)[resource.image1 == ""],'withImage2': (True, False)[resource.image2 == ""],
        'url': resource.url,'license': resource.license, 'choices': choices, 'theme': resource.theme.all,'organisation': resource.organisation.all,
        'audience' : resource.audience.all, 'publisher': resource.publisher, 'year_of_publication': resource.datePublished,
        'authors': resource.authors.all, 'authorsCollection': authorsCollection,
        'image_credit1': resource.imageCredit1,'image_credit2': resource.imageCredit2,
        'category': getCategory(resource.category), 'categorySelected': resource.category.id,
        'education_level': educationLevel, 'educationLevelSelected': resource.educationLevel,
        'learning_resource_type': learningResourceType, 'learningResourceTypeSelected': resource.learningResourceType,
        'time_required': resource.timeRequired, 'conditions_of_access': resource.conditionsOfAccess
    })

    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            images = []
            image1_path = saveImage(request, form, 'image1','1')
            image2_path = saveImage(request, form, 'image2','2')
            images.append(image1_path)
            images.append(image2_path)
            form.save(request, images)
            if(isTrainingResource):
                return redirect('/training_resource/' + str(pk))
            return redirect('/resource/' + str(pk))

    return render(request, 'editResource.html', {'form': form, 'resource': resource, 'curatedGroups': curatedGroups,
     'user': user, 'settings': settings, 'permissionForm': permissionForm, 'isTrainingResource': isTrainingResource })

def deleteResource(request, pk, isTrainingResource):
    obj = get_object_or_404(Resource, id=pk)
    if request.user == obj.creator or request.user.is_staff or request.user.id in getCooperators(pk):
        obj.delete()
        reviews = Review.objects.filter(content_type=ContentType.objects.get(model="resource"), object_pk=pk)
        for r in reviews:
            r.delete()
    if(isTrainingResource):
        return redirect('training_resources')
    return redirect('resources')

def tresources_autocomplete(request):
    return resources_autocomplete(request, True)

def resources_autocomplete(request, isTrainingResource=False):
    resources = preFilteredResources(request)
    if request.GET.get('q'):
        text = request.GET['q']
        resourceNames = resources.filter( Q(name__icontains = text) ).filter(isTrainingResource=isTrainingResource).distinct()
        resourceKeywords = resources.filter( Q(keywords__keyword__icontains = text) ).filter(isTrainingResource=isTrainingResource).distinct()
        rsc_names = resourceNames.values_list('name',flat=True).distinct()
        keywords = resourceKeywords.values_list('keywords__keyword',flat=False).distinct()
        keywords = Keyword.objects.filter(keyword__in = keywords).values_list('keyword',flat=True).distinct()
        report = chain(rsc_names, keywords)
        json = list(report)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")

def getRscNamesKeywords(text):
    rsc_names = Resource.objects.filter(name__icontains=text).values_list('name',flat=True).distinct()
    keywords = Keyword.objects.filter(keyword__icontains=text).values_list('keyword',flat=True).distinct()
    report = chain(rsc_names, keywords)
    return report

def getOtherUsers(creator):
    users = list(User.objects.all().exclude(is_superuser=True).exclude(id=creator.id).values_list('name','email'))
    return users

def getCooperators(resourceID):
    users = list(ResourcePermission.objects.all().filter(resource_id=resourceID).values_list('user',flat=True))
    return users

def getCooperatorsEmail(resourceID):
    users = getCooperators(resourceID)
    cooperators = ""
    for user in users:
        userObj = get_object_or_404(User, id=user)
        cooperators += userObj.email + ", "
    return cooperators

def clearFilters(request):
    return redirect ('resources')

def saveImage(request, form, element, ref):
    image_path = ''
    filepath = request.FILES.get(element, False)
    withImage = form.cleaned_data.get('withImage' + ref)
    if (filepath):
        x = form.cleaned_data.get('x' + ref)
        y = form.cleaned_data.get('y' + ref)
        w = form.cleaned_data.get('width' + ref)
        h = form.cleaned_data.get('height' + ref)
        photo = request.FILES[element]
        image = Image.open(photo)
        cropped_image = image.crop((x, y, w+x, h+y))
        if(ref == '2'):
            finalSize = (1100, 400)
        else:
            finalSize = (600, 400)
        
        resized_image = cropped_image.resize(finalSize, Image.ANTIALIAS)

        if(cropped_image.width > image.width):
            size = (abs(int((finalSize[0]-(finalSize[0]/cropped_image.width*image.width))/2)), finalSize[1])
            whitebackground = Image.new(mode='RGBA',size=size,color=(255,255,255,0))
            position = ((finalSize[0] - whitebackground.width), 0)
            resized_image.paste(whitebackground, position)
            position = (0, 0)
            resized_image.paste(whitebackground, position)
        
        if(cropped_image.height > image.height):
            size = (finalSize[0], abs(int((finalSize[1]-(finalSize[1]/cropped_image.height*image.height))/2)))
            whitebackground = Image.new(mode='RGBA',size=size,color=(255,255,255,0))
            position = (0, (finalSize[1] - whitebackground.height))
            resized_image.paste(whitebackground, position)
            position = (0, 0)
            resized_image.paste(whitebackground, position)

        image_path = saveImageWithPath(resized_image, photo.name)
    elif withImage:
            image_path = '/'
    else:
        image_path = ''
    return image_path

def saveImageWithPath(image, photoName):
    _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
    random_num = random.randint(0, 1000)
    image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photoName
    image.save(image_path)
    image_path = '/' + image_path
    return image_path

def preFilteredResources(request):
    resources = Resource.objects.all().order_by('id')
    return applyFilters(request, resources)

def applyFilters(request, resources):
    approvedResources = ApprovedResources.objects.all().values_list('resource_id',flat=True)

    if request.GET.get('language'):
        resources = resources.filter(inLanguage = request.GET['language'])
    if request.GET.get('license'):
        resources = resources.filter(license__icontains = request.GET['license'])
    if request.GET.get('theme'):
        resources = resources.filter(theme = request.GET['theme'])
    if request.GET.get('category'):
        resources = resources.filter(category = request.GET['category'])
    if request.GET.get('approvedCheck'):
        if request.GET['approvedCheck'] == 'On':
            resources = resources.filter(id__in=approvedResources)
        if request.GET['approvedCheck'] == 'Off':
            resources = resources.exclude(id__in=approvedResources)
        if request.GET['approvedCheck'] == 'All':
            resources = resources
    else:
        resources = resources.filter(id__in=approvedResources)

    return resources

def setFilters(request, filters):
    if request.GET.get('language'):
        filters['language'] = request.GET['language']
    if request.GET.get('license'):
        filters['license'] = request.GET['license']
    if request.GET.get('theme'):
        filters['theme'] = int(request.GET['theme'])
    if request.GET.get('category'):
        filters['category'] = int(request.GET['category'])
    if request.GET.get('approvedCheck'):
        filters['approvedCheck'] = request.GET['approvedCheck']
    return filters


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

@staff_member_required()
def setApprovedRsc(request):
    response = {}
    id = request.POST.get("resource_id")
    approved = request.POST.get("approved")
    setResourceApproved(id, approved)
    return JsonResponse(response, safe=False)



def setResourceApproved(id, approved):
    approved= False if approved in ['False','false','0'] else True
    aResource = get_object_or_404(Resource, id=id)
    if approved == True:
        #Insert
        ApprovedResources.objects.get_or_create(resource=aResource)
        #Delete UnApprovedResources
        try:
            obj = UnApprovedResources.objects.get(resource_id=id)
            obj.delete()
        except UnApprovedResources.DoesNotExist:
            print("Does not exist this unapproved resource")
    else:
        #Insert UnApprovedResources
        UnApprovedResources.objects.get_or_create(resource=aResource)
        #Delete
        try:
            obj = ApprovedResources.objects.get(resource_id=id)
            obj.delete()
        except ApprovedResources.DoesNotExist:
            print("Does not exist this approved resource")

def setSavedResource(request):
    response = {}
    resourceId = request.POST.get("resource_id")
    userId = request.POST.get("user_id")
    save = request.POST.get("save")
    saveResource(resourceId, userId, save)
    return JsonResponse(response, safe=False)


def saveResource(resourceId, userId, save):
    save= False if save in ['False','false','0'] else True
    fResource = get_object_or_404(Resource, id=resourceId)
    fUser = get_object_or_404(User, id=userId)
    if save == True:
        #Insert
        savedResource = SavedResources.objects.get_or_create(resource=fResource, user=fUser)
    else:
        #Delete
        try:
            obj = SavedResources.objects.get(resource_id=resourceId,user_id=userId)
            obj.delete()
        except SavedResources.DoesNotExist:
            print("Does not exist this resource saved")


@staff_member_required()
def setHiddenResource(request):
    response = {}
    id = request.POST.get("resource_id")
    hidden = request.POST.get("hidden")
    setResourceHidden(id, hidden)
    return JsonResponse(response, safe=False)

def setResourceHidden(id, hidden):
    resource = get_object_or_404(Resource, id=id)
    resource.hidden = False if hidden in ['False','false','0'] else True
    resource.save()

@staff_member_required()
def setFeaturedResource(request):
    response = {}
    id = request.POST.get("resource_id")
    featured = request.POST.get("featured")
    setResourceFeatured(id, featured)
    return JsonResponse(response, safe=False)

def setResourceFeatured(id, featured):
    resource = get_object_or_404(Resource, id=id)
    resource.featured = featured
    resource.featured = False if featured in ['False','false','0'] else True
    resource.save()

@staff_member_required()
def setTraining(request):
    response = {}
    id = request.POST.get("resource_id")
    status = request.POST.get("status")
    print(status)
    resource = get_object_or_404(Resource, id=id)
    resource.isTrainingResource = status
    resource.save()

    return JsonResponse(response,safe=False)



def allowUserResource(request):
    response = {}
    resourceId = request.POST.get("resource_id")
    users = request.POST.get("users")
    resource = get_object_or_404(Resource, id=resourceId)

    if request.user != resource.creator and not request.user.is_staff:
        #TODO return JsonResponse with error code
        return redirect('../resources', {})

    #Delete all
    objs = ResourcePermission.objects.all().filter(resource_id=resourceId)
    if(objs):
        for obj in objs:
            obj.delete()

    #Insert all
    users = users.split(',')
    for user in users:
        fUser = User.objects.filter(email=user)[:1].get()
        resourcePermission = ResourcePermission(resource=resource, user=fUser)
        resourcePermission.save()

    return JsonResponse(response, safe=False)

def resource_review(request, pk):
    return render(request, 'resource_review.html', {'resourceID': pk})


### Download all resources in a CSV file
def downloadResources(request):
    resources = Resource.objects.get_queryset()

    response = StreamingHttpResponse(
        streaming_content=(iter_items(resources, Buffer())),
        content_type='text/csv',
    )
    response['Content-Disposition'] = 'attachment; filename="resources.csv"'
    return response

def get_headers():
    return ['id', 'name', 'abstract', 'audience', 'keywords','inLanguage', 'category', 'url', 'license', 'authors',
     'publisher', 'datePublished', 'theme', 'resourceDOI']

def get_data(item):
    keywordsList = list(item.keywords.all().values_list('keyword', flat=True))
    authorsList = list(item.authors.all().values_list('author', flat=True))
    audienceList = list(item.audience.all().values_list('audience', flat=True))
    themeList = list(item.theme.all().values_list('theme', flat=True))

    return {
        'id': item.id,
        'name': item.name,
        'abstract': item.abstract,
        'audience': audienceList,
        'keywords': keywordsList,
        'inLanguage': item.inLanguage,
        'category': item.category,
        'url': item.url,
        'license': item.license,
        'authors': authorsList,
        'publisher': item.publisher,
        'datePublished': item.datePublished,
        'theme': themeList,
        'resourceDOI': item.resourceDOI,
    }

class Buffer(object):
    def write(self, value):
        return value

def iter_items(items, pseudo_buffer):
    writer = csv.DictWriter(pseudo_buffer, fieldnames=get_headers())
    yield ','.join(get_headers()) + '\r\n'

    for item in items:
        yield writer.writerow(get_data(item))


def getResourceKeywordsSelector(request):
    resource_id = request.GET.get("resource_id")
    keywordsSelected = []
    if resource_id != '0':
        resource = get_object_or_404(Resource, id=resource_id)
        keywordsSelected = list(resource.keywords.all().values_list('keyword', flat=True))

    options = '<select id="id_keywords" class="select form-control">'
    response = {}
    keywords = Keyword.objects.get_queryset()
    keywords = keywords.values_list("id","keyword")
    keywords = tuple(keywords)
    if keywords:
        for keyword in keywords:
            found = False
            if(keywordsSelected):
                for key in keywordsSelected:
                    if(str(keyword[1]) == key):
                        found=True
                        options += '<option value = "%s" selected>%s</option>' % (
                            keyword[0],
                            keyword[1]
                        )
                        break
            if(not found or not keywordsSelected):
                options += '<option value = "%s">%s</option>' % (
                    keyword[0],
                    keyword[1]
                )
        options += '</select>'
        response['keywords'] = options
    else:
        response['keywords'] = '<select id="id_keywords" class="select form-control" disabled></select>'

    return JsonResponse(response)


def getResourceAuthorsSelector(request):
    resource_id = request.GET.get("resource_id")
    authorsSelected = []
    if resource_id != '0':
        resource = get_object_or_404(Resource, id=resource_id)
        authorsSelected = list(resource.authors.all().values_list('author', flat=True))

    options = '<select id="id_authors" class="select form-control">'
    response = {}
    authors = Author.objects.get_queryset()
    authors = authors.values_list("id","author")
    authors = tuple(authors)
    if authors:
        for author in authors:
            found = False
            if(authorsSelected):
                for key in authorsSelected:
                    if(str(author[1]) == key):
                        found=True
                        options += '<option value = "%s" selected>%s</option>' % (
                            author[0],
                            author[1]
                        )
                        break
            if(not found or not authorsSelected):
                options += '<option value = "%s">%s</option>' % (
                    author[0],
                    author[1]
                )
        options += '</select>'
        response['authors'] = options
    else:
        response['authors'] = '<select id="id_authors" class="select form-control" disabled></select>'

    return JsonResponse(response)
