from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.db.models import Q, Avg
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.utils import formats
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from authors.models import Author
from PIL import Image
from datetime import datetime
from reviews.models import Review
from .models import Resource, Keyword, ApprovedResources, SavedResources, BookmarkedResources, Theme, Category
from .models import ResourcesGrouped, ResourcePermission, EducationLevel, LearningResourceType, UnApprovedResources
from .models import Audience
from .forms import ResourceForm, ResourcePermissionForm
import copy
import csv
import random
from rest_framework import status

User = get_user_model()


def training_resources(request):
    return resources(request, True)


def resources(request, isTrainingResource=False):
    user = request.user
    if(isTrainingResource):
        resources = Resource.objects.all().filter(isTrainingResource=True).order_by('-dateUpdated')
        languagesWithContent = Resource.objects.all().filter(
                isTrainingResource=True).values_list('inLanguage', flat=True).distinct()
        endPoint = 'training_resources'
    else:
        resources = Resource.objects.all().filter(isTrainingResource=False).order_by('-dateUpdated')
        languagesWithContent = Resource.objects.all().filter(
                isTrainingResource=False).values_list('inLanguage', flat=True).distinct()
        endPoint = 'resources'

    themes = Theme.objects.all()
    categories = Category.objects.all()
    audiencies = Audience.objects.all()

    filters = {'keywords': '', 'inLanguage': ''}
    resources = applyFilters(request, resources)
    filters = setFilters(request, filters)
    resources = resources.distinct()
    resources = resources.filter(~Q(hidden=True))

    if not user.is_staff:
        resources = resources.filter(approved=True)

    # Ordering
    if request.GET.get('orderby'):
        orderBy = request.GET.get('orderby')
        if("featured" in orderBy):
            resourcesTop = resources.filter(featured=True)
            resourcesTopIds = list(resourcesTop.values_list('id', flat=True))
            resources = resources.exclude(id__in=resourcesTopIds)
            resources = list(resourcesTop) + list(resources)
        elif("avg" in orderBy):
            reviews = Review.objects.filter(content_type=ContentType.objects.get(model="resource"))
            reviews = reviews.values(
                    "object_pk",
                    "content_type").annotate(avg_rating=Avg('rating')).order_by(orderBy).values_list(
                            'object_pk', flat=True)
            reviews = list(reviews)
            resourcesVoted = []
            for r in reviews:
                rsc = Resource.objects.get(pk=r)
                if rsc in resources:
                    resourcesVoted.append(rsc)
            resources = resources.exclude(id__in=reviews)
            resources = list(resourcesVoted) + list(resources)
        else:
            resources = resources.order_by('-dateUpdated')
        filters['orderby'] = request.GET['orderby']
    else:
        resources = resources.order_by('-dateUpdated')

    counter = len(resources)
    paginator = Paginator(resources, 16)
    page = request.GET.get('page')
    resources = paginator.get_page(page)

    return render(request, 'resources.html', {
        'resources': resources,
        # 'approvedResources': approvedResources,
        # 'unApprovedResources': unApprovedResources,
        'counter': counter,
        # 'savedResources': savedResources,
        # 'bookmarkedResources': bookmarkedResources,
        'filters': filters,
        'settings': settings,
        'languagesWithContent': languagesWithContent,
        'themes': themes,
        'categories': categories,
        'audiencies': audiencies,
        'isTrainingResource': isTrainingResource,
        'endPoint': endPoint,
        'isSearchPage': True})


@login_required(login_url='/login')
def newTrainingResource(request):
    return newResource(request, True)


@login_required(login_url='/login')
def newResource(request, isTrainingResource=False):
    form = ResourceForm()
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            images = []
            image1_path = saveImage(request, form, 'image1', '1')
            image2_path = saveImage(request, form, 'image2', '2')
            images.append(image1_path)
            images.append(image2_path)
            isTrainingResource = request.POST.get('trainingResource')
            form.save(request, images)

            to = copy.copy(settings.EMAIL_RECIPIENT_LIST)
            to.append(request.user.email)
            if(isTrainingResource):
                messages.success(request, _('Training resource added correctly'))
                subject = 'New training resource submitted'
                message = render_to_string('emails/new_training_resource.html', {"domain": settings.HOST})
                email = EmailMessage(subject, message, to=to)
                email.content_subtype = "html"
                email.send()
                return redirect('/training_resources')
            messages.success(request, _('Resource added correctly'))
            subject = 'New resource submitted'
            message = render_to_string('emails/new_resource.html', {"domain": settings.HOST})
            email = EmailMessage(subject, message, to=to)
            email.content_subtype = "html"
            email.send()
            return redirect('/resources')

    return render(request, 'resource_form.html', {
        'form': form,
        'settings': settings,
        'isTrainingResource': isTrainingResource})


def training_resource(request, pk):
    return resource(request, pk)


def resource(request, pk):
    resource = get_object_or_404(Resource, id=pk)
    isTrainingResource = resource.isTrainingResource
    user = request.user

    if(isTrainingResource):
        endPoint = '/training_resources'
    else:
        endPoint = '/resources'

    previous_page = request.META.get('HTTP_REFERER')
    if previous_page and 'review' in previous_page:
        # Send email
        to = copy.copy(settings.EMAIL_RECIPIENT_LIST)
        to.append(resource.creator.email)
        if resource.isTrainingResource:
            subject = 'Your training resource has received a review'
            message = render_to_string('emails/training_resource_review.html', {
                "domain": settings.HOST,
                "name": resource.name,
                "id": pk})
            email = EmailMessage(subject, message, to=to)
            email.content_subtype = "html"
            email.send()
        else:
            subject = 'Your resource has received a review'
            message = render_to_string('emails/resource_review.html', {
                "domain": settings.HOST,
                "name": resource.name,
                "id": pk})
            email = EmailMessage(subject, message, to=to)
            email.content_subtype = "html"
            email.send()

    users = getOtherUsers(resource.creator)
    cooperators = getCooperatorsEmail(pk)
    unApprovedResources = UnApprovedResources.objects.all().values_list('resource_id', flat=True)
    # TODO: Review this if
    if (
            resource.id in unApprovedResources or resource.hidden) and (
                    user.is_anonymous or (
                        user != resource.creator and (not user.is_staff and user.id in getCooperators(pk)))):
        return redirect('../resources', {})
    permissionForm = ResourcePermissionForm(initial={
        'usersCollection': users,
        'selectedUsers': cooperators})
    savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list(
            'resource_id', flat=True)
    bookmarkedResource = BookmarkedResources.objects.all().filter(user_id=user.id, resource_id=pk).exists()

    # TODO: Only ask for the resource
    approvedResources = ApprovedResources.objects.all().values_list('resource_id', flat=True)
    return render(request, 'resource.html', {
        'resource': resource,
        'savedResources': savedResources,
        'bookmarkedResource': bookmarkedResource,
        'approvedResources': approvedResources,
        'unApprovedResources': unApprovedResources,
        'cooperators': getCooperators(pk),
        'permissionForm': permissionForm,
        'isTrainingResource': isTrainingResource,
        'endPoint': endPoint,
        'isSearchPage': True})


def editTrainingResource(request, pk):
    return editResource(request, pk)


def editResource(request, pk):
    resource = get_object_or_404(Resource, id=pk)
    isTrainingResource = resource.isTrainingResource
    user = request.user
    cooperators = getCooperators(pk)
    # TODO: This better
    if user != resource.creator and not user.is_staff and user.id not in cooperators:
        if(isTrainingResource):
            return redirect('/training_resources')
        return redirect('../resources', {})

    curatedGroups = list(ResourcesGrouped.objects.all().filter(resource_id=pk).values_list('group_id', flat=True))

    # TODO: is needed with image?
    form = ResourceForm(initial={
        # Main information, mandatory
        'name': resource.name,
        'url': resource.url,
        'keywords': resource.keywords.all,
        'abstract': resource.abstract,
        'description_citizen_science_aspects': resource.description_citizen_science_aspects,
        'category': getCategory(resource.category),
        'categorySelected': resource.category.id,
        'audience': resource.audience.all,
        'theme': resource.theme.all,
        # Publish information
        'authors': resource.authors.all,
        'publisher': resource.publisher,
        'year_of_publication': resource.datePublished,
        'resource_DOI': resource.resourceDOI,
        'license': resource.license,
        # Training related fields
        'education_level': resource.educationLevel.all,
        'learning_resource_type': resource.learningResourceType.all,
        'time_required': resource.timeRequired,
        'conditions_of_access': resource.conditionsOfAccess,
        # Links
        'project': resource.project.all,
        'organisation': resource.organisation.all,
        # Images
        'image_credit1': resource.imageCredit1,
        'image_credit2': resource.imageCredit2,
        'image1': resource.image1,
        'image2': resource.image2,
        'withImage1': (True, False)[resource.image1 == ""],
        'withImage2': (True, False)[resource.image2 == ""],
    })

    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            images = []
            image1_path = saveImage(request, form, 'image1', '1')
            image2_path = saveImage(request, form, 'image2', '2')
            images.append(image1_path)
            images.append(image2_path)
            form.save(request, images)
            if(isTrainingResource):
                return redirect('/training_resource/' + str(pk))
            return redirect('/resource/' + str(pk))

    return render(request, 'resource_form.html', {
        'form': form,
        'resource': resource,
        'curatedGroups': curatedGroups,
        'user': user,
        'settings': settings,
        'isTrainingResource': isTrainingResource})


def saveResourceAjax(request):
    print(request.POST)
    request.POST = request.POST.copy()
    request.POST = updateKeywords(request.POST)
    request.POST = updateAuthors(request.POST)
    request.POST = updateEducationLevel(request.POST)
    request.POST = updateLearningResourceType(request.POST)
    form = ResourceForm(request.POST, request.FILES)
    if form.is_valid():
        images = setImages(request, form)
        pk = form.save(request, images)
        if pk and not request.POST.get('resourceID').isnumeric():
            sendResourceEmail(pk, request.user)
        return JsonResponse({'ResourceCreated': 'OK', 'Resource': pk}, status=status.HTTP_200_OK)
    else:
        return JsonResponse(form.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


def updateKeywords(dictio):
    keywords = dictio.pop('keywords', None)
    if(keywords):
        for k in keywords:
            if not k.isdecimal():
                # This is a new keyword
                Keyword.objects.get_or_create(keyword=k)
                keyword_id = Keyword.objects.get(keyword=k).id
                dictio.update({'keywords': keyword_id})
            else:
                # This keyword is already in the database
                dictio.update({'keywords': k})
    return dictio


def updateAuthors(dictio):
    authors = dictio.pop('authors', None)
    if(authors):
        for a in authors:
            if not a.isdecimal():
                # This is a new author
                Author.objects.get_or_create(author=a)
                author_id = Author.objects.get(author=a).id
                dictio.update({'authors': author_id})
            else:
                # This author is already in the database
                dictio.update({'author': a})
    return dictio


def updateEducationLevel(dictio):
    education_level = dictio.pop('education_level', None)
    if(education_level):
        for e in education_level:
            if not e.isdecimal():
                # This is a new education level
                EducationLevel.objects.get_or_create(educationLevel=e)
                educationLevel_id = EducationLevel.objects.get(educationLevel=e).id
                dictio.update({'education_level': educationLevel_id})
            else:
                # This author is already in the database
                dictio.update({'education_level': e})
    return dictio


def updateLearningResourceType(dictio):
    learning_resource_type = dictio.pop('learning_resource_type', None)
    if(learning_resource_type):
        for le in learning_resource_type:
            if not le.isdecimal():
                # This is a new learning resource type
                LearningResourceType.objects.get_or_create(learningResourceType=le)
                learningResourceType_id = LearningResourceType.objects.get(learningResourceType=le).id
                dictio.update({'learning_resource_type': learningResourceType_id})
            else:
                # This author is already in the database
                dictio.update({'learning_resource_type': le})

    return dictio


def setImages(request, form):
    print('setImages')
    images = []
    image1_path = saveImage(request, form, 'image1', '1')
    image2_path = saveImage(request, form, 'image2', '2')
    images.append(image1_path)
    images.append(image2_path)
    print(images)
    return images


def sendResourceEmail(id, user):
    return 0


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


def trainingsAutocompleteSearch(request):
    return resourcesAutocompleteSearch(request, True)


def resourcesAutocompleteSearch(request, isTrainingResource=False):
    if request.GET.get('q'):
        text = request.GET['q']
        resources = getResourcesAutocomplete(text, isTrainingResource)
        resources = list(resources)
        return JsonResponse(resources, safe=False)
    else:
        return HttpResponse("No cookies")


def getResourcesAutocomplete(text, isTrainingResource=False):
    approvedResources = ApprovedResources.objects.all().values_list('resource_id', flat=True)
    resources = Resource.objects.filter(~Q(hidden=True)).filter(
            id__in=approvedResources).filter(
                    isTrainingResource=isTrainingResource).filter(
                            name__icontains=text).values_list('id', 'name').distinct()
    keywords = Keyword.objects.filter(
            keyword__icontains=text).values_list('keyword', flat=True).distinct()
    report = []
    for resource in resources:
        if isTrainingResource:
            report.append({"type": "training", "id": resource[0], "text": resource[1]})
        else:
            report.append({"type": "resource", "id": resource[0], "text": resource[1]})
    for keyword in keywords:
        numberElements = Resource.objects.filter(
                Q(keywords__keyword__icontains=keyword)).filter(
                        isTrainingResource=isTrainingResource).count()
        report.append({"type": "keyword", "text": keyword, "numberElements": numberElements})
    return report


def getOtherUsers(creator):
    users = list(User.objects.all().exclude(is_superuser=True).exclude(id=creator.id).values_list('name', 'email'))
    return users


def getCooperators(resourceID):
    users = list(ResourcePermission.objects.all().filter(resource_id=resourceID).values_list('user', flat=True))
    return users


def getCooperatorsEmail(resourceID):
    users = getCooperators(resourceID)
    cooperators = ""
    for user in users:
        userObj = get_object_or_404(User, id=user)
        cooperators += userObj.email + ", "
    return cooperators


def clearFilters(request):
    return redirect('resources')


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
            whitebackground = Image.new(mode='RGBA', size=size, color=(255, 255, 255, 0))
            position = ((finalSize[0] - whitebackground.width), 0)
            resized_image.paste(whitebackground, position)
            position = (0, 0)
            resized_image.paste(whitebackground, position)
        if(cropped_image.height > image.height):
            size = (finalSize[0], abs(int((finalSize[1]-(finalSize[1]/cropped_image.height*image.height))/2)))
            whitebackground = Image.new(mode='RGBA', size=size, color=(255, 255, 255, 0))
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
    image_path = "images/" + _datetime + '_' + str(random_num) + '_' + photoName
    image.save("media/"+image_path)
    return image_path


def preFilteredResources(request):
    resources = Resource.objects.all().order_by('id')
    return applyFilters(request, resources)


def applyFilters(request, resources):
    approvedResources = ApprovedResources.objects.all().values_list('resource_id', flat=True)

    if request.GET.get('keywords'):
        resources = resources.filter(
                Q(name__icontains=request.GET['keywords']) |
                Q(keywords__keyword__icontains=request.GET['keywords'])).distinct()
    if request.GET.get('inLanguage'):
        resources = resources.filter(inLanguage=request.GET['inLanguage'])
    if request.GET.get('license'):
        resources = resources.filter(license__icontains=request.GET['license'])
    if request.GET.get('theme'):
        resources = resources.filter(theme__theme=request.GET['theme'])
    if request.GET.get('category'):
        resources = resources.filter(category__text=request.GET['category'])
    if request.GET.get('audience'):
        resources = resources.filter(audience__audience=request.GET['audience'])
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
    if request.GET.get('keywords'):
        filters['keywords'] = request.GET['keywords']
    if request.GET.get('inLanguage'):
        filters['inLanguage'] = request.GET['inLanguage']
    if request.GET.get('audience'):
        filters['audience'] = request.GET['audience']
    if request.GET.get('license'):
        filters['license'] = request.GET['license']
    if request.GET.get('theme'):
        filters['theme'] = request.GET['theme']
    if request.GET.get('category'):
        filters['category'] = request.GET['category']
    if request.GET.get('approvedCheck'):
        filters['approvedCheck'] = request.GET['approvedCheck']
    print(filters)
    return filters


def get_sub_category(request):
    category = request.GET.get("category")
    options = '<select id="id_subcategory" class="select form-control">'
    response = {}

    if category:
        sub_categories = Category.objects.filter(parent=category)
        sub_categories = sub_categories.values_list("id", "text")
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


def bookmarkResource(request):
    response = {}
    resourceId = request.POST.get("resourceId")
    fResource = get_object_or_404(Resource, id=resourceId)
    user = request.user
    bookmark = False if request.POST.get("bookmark") in ['false'] else True
    if bookmark:
        BookmarkedResources.objects.get_or_create(resource=fResource, user=user)
        response = {"created": "OK", "resource": fResource.name}
    else:
        try:
            obj = BookmarkedResources.objects.get(resource_id=resourceId, user_id=user.id)
            obj.delete()
            response = {"success": "Bookmark deleted"}
        except BookmarkedResources.DoesNotExist:
            response = {"error": "Doen not exits"}

    return JsonResponse(response, safe=False)


@staff_member_required()
def approveResource(request):
    resourceId = request.POST.get("resourceId")
    resource = get_object_or_404(Resource, id=resourceId)
    if request.POST.get("approved") in ['true']:
        resource.approved = True
    else:
        resource.approved = False
    resource.moderated = True
    resource.save()

    return JsonResponse({"success": "Updated aproval"}, safe=False)


@staff_member_required()
def setFeaturedResource(request):
    resourceId = request.POST.get("resourceId")
    resource = get_object_or_404(Resource, id=resourceId)
    if request.POST.get("featured") in ['true']:
        resource.featured = True
    else:
        resource.featured = False
    resource.save()

    return JsonResponse({"success": "Updated featured resource"}, safe=False)


@staff_member_required()
def setTrainingResource(request):
    resourceId = request.POST.get("resourceId")
    resource = get_object_or_404(Resource, id=resourceId)
    if request.POST.get("isTraining") in ['true']:
        resource.isTrainingResource = True
    else:
        resource.isTrainingResource = False
    resource.save()

    return JsonResponse({"success": "Updated training resource"}, safe=False)


def abookmarkResource(resourceId, userId, save):
    save = False if save in ['False', 'false', '0'] else True
    fResource = get_object_or_404(Resource, id=resourceId)
    fUser = get_object_or_404(User, id=userId)
    if save is True:
        # Insert
        SavedResources.objects.get_or_create(resource=fResource, user=fUser)
        # sendEmail
        to = copy.copy(settings.EMAIL_RECIPIENT_LIST)
        to.append(fResource.creator.email)
        if fResource.isTrainingResource:
            subject = 'Your training resource has been added to a library'
            message = render_to_string('emails/library_training_resource.html', {
                "domain": settings.HOST,
                "name": fResource.name,
                "id": resourceId})
            email = EmailMessage(subject, message, to=to)
            email.content_subtype = "html"
            email.send()
        else:
            subject = 'Your resource has been added to a library'
            message = render_to_string('emails/library_resource.html', {
                "domain": settings.HOST,
                "name": fResource.name,
                "id": resourceId})
            email = EmailMessage(subject, message, to=to)
            email.content_subtype = "html"
            email.send()
    else:
        # Delete
        try:
            obj = SavedResources.objects.get(resource_id=resourceId, user_id=userId)
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
    resource.hidden = False if hidden in ['False', 'false', '0'] else True
    resource.save()


@staff_member_required()
def setTraining(request):
    response = {}
    id = request.POST.get("resource_id")
    status = request.POST.get("status")
    resource = get_object_or_404(Resource, id=id)
    resource.isTrainingResource = status
    resource.save()
    return JsonResponse(response, safe=False)


@staff_member_required()
def setOwnTraining(request):
    response = {}
    id = request.POST.get("resource_id")
    status = request.POST.get("status")
    resource = get_object_or_404(Resource, id=id)
    resource.own = status
    resource.save()
    return JsonResponse(response, safe=False)


def allowUserResource(request):
    response = {}
    resourceId = request.POST.get("resource_id")
    users = request.POST.get("users")
    resource = get_object_or_404(Resource, id=resourceId)

    if request.user != resource.creator and not request.user.is_staff:
        # TODO return JsonResponse with error code
        return redirect('../resources', {})

    # Delete all
    objs = ResourcePermission.objects.all().filter(resource_id=resourceId)
    if(objs):
        for obj in objs:
            obj.delete()

    # Insert all
    users = users.split(',')
    for user in users:
        fUser = User.objects.filter(email=user)[:1].get()
        resourcePermission = ResourcePermission(resource=resource, user=fUser)
        resourcePermission.save()

    return JsonResponse(response, safe=False)


def resource_review(request, pk):
    return render(request, 'resource_review.html', {'resourceID': pk})


# Download all resources in a CSV file
def downloadResources(request):
    resources = Resource.objects.get_queryset()

    response = StreamingHttpResponse(
        streaming_content=(iter_items(resources, Buffer())),
        content_type='text/csv',
    )
    response['Content-Disposition'] = 'attachment; filename="resources.csv"'
    return response


def get_headers():
    return [
            'id', 'name', 'abstract', 'audience', 'keywords', 'inLanguage',
            'category', 'url', 'license', 'authors', 'publisher',
            'datePublished', 'theme', 'resourceDOI']


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
