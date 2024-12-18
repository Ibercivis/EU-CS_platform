from django.shortcuts import render
from django.conf import settings
from django.core.mail import EmailMessage
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import formats
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from rest_framework import status
from django.db.models import Q
from resources.models import Resource
from projects.models import Project
from organisations.models import Organisation
from profiles.models import Profile
from django.template.response import TemplateResponse


from datetime import datetime
from PIL import Image

from .forms import PlatformForm
from .models import HelpText, Platform
import copy
import random


# Create your views here.


@login_required(login_url='/login')
def newPlatform(request):
    user = request.user
    text = get_object_or_404(HelpText, slug='new-platform')
    platformForm = PlatformForm()

    return TemplateResponse(request, 'platform_form.html', {'form': platformForm, 'text': text, 'user': user})


@login_required(login_url='/login')
def editPlatform(request, pk):
    user = request.user
    platform = get_object_or_404(Platform, id=pk)

    if user != platform.creator and not user.is_staff:
        return redirect('../platforms', {})
    
    platformForm = PlatformForm(instance=platform)

    platformForm.initial.update({
        'name': platform.name,
        'url': platform.url,
        'geographicExtend': platform.geographicExtend,
        'countries': platform.countries,
        'platformLocality': platform.platformLocality,
        'contactPoint': platform.contactPoint,
        'contactPointEmail': platform.contactPointEmail,
        'organisation': platform.organisation.all,
        'logo': platform.logo,
        'logoCredit': platform.logoCredit,
        'profileImage': platform.profileImage,
        'profileImageCredit': platform.profileImageCredit
    })
    return render(request, 'platform_form.html', {'form': platformForm, 'user': user, 'id': platform.id})


@login_required(login_url='/login')
def deletePlatformAjax(request, pk):
    print(pk)
    print(request.user)
    platform = get_object_or_404(Platform, id=pk)
    print(platform.creator)
    if request.user == platform.creator or request.user.is_staff:
        platform.delete()
        return JsonResponse({'Platform deleted': 'OK', 'Id': pk}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({}, status=status.HTTP_403.FORBIDDEN)


@login_required(login_url='/login')
def savePlatformAjax(request):
    request.POST = request.POST.copy()
    print("Sent data", request.POST)
    print("Sent files", request.FILES)

    platform_instance = None
    if request.POST.get('Id').isnumeric():
        platform_instance = get_object_or_404(Platform, id=request.POST['Id'])

    # Create a form instance and populate it with data from the request:
    form = PlatformForm(request.POST, request.FILES, instance=platform_instance)
    
    if form.is_valid():
        images = setImages(request, form)
        pk = form.save(request, images)

        # Send email to user only if the platform is new
        if not platform_instance:
            sendPlatformEmail(pk, request.user)

        return JsonResponse({'Created': 'OK', 'Id': pk}, status=status.HTTP_200_OK)
    else:
        print("Form errors:", form.errors)
        return JsonResponse(form.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


def platform(request, pk):
    platform = get_object_or_404(Platform, id=pk)
    return render(request, 'platform.html', {'platform': platform})


def platforms(request):
    platforms = Platform.objects.get_queryset()
    totalCount = len(platforms)
    filters = {'keywords': '', 'country': '', 'geographicExtend': ''}
    countriesWithContent = Platform.objects.values_list('countries', flat=True).distinct()
    geographicExtendsWithContent = Platform.objects.values_list('geographicExtend', flat=True).distinct()
    platforms = applyFilters(request, platforms)
    filters = setFilters(request, filters)
    platforms = platforms.distinct()

    if request.GET.get('orderby'):
        orderBy = request.GET.get('orderby')
        if ("name" in orderBy):
            platforms = platforms.order_by('name')
    else:
        platforms = platforms.order_by('-dateUpdated')

    counter = len(platforms)
    counterPlatforms = len(platforms)

    #To Count
    #For resources count
    allResources = Resource.objects.all()
    allResources = applyFilters(request, allResources)
    allResources = allResources.distinct()
    resources2 = allResources.filter(~Q(isTrainingResource=True))
    trainingResources = allResources.filter(isTrainingResource=True)
    resourcesCounter = len(resources2)
    trainingResourcesCounter = len(trainingResources)

    #For projects count
    projects = Project.objects.all()
    projects = projects.filter(~Q(hidden=True))
    projects = applyFilters(request, projects)
    projects = projects.distinct()
    projectsCounter = len(projects)

    #For organisations count
    organisations = Organisation.objects.all()
    organisations = applyFilters(request, organisations)
    organisations = organisations.distinct()
    organisationsCounter = len(organisations)

    #For users count
    users = Profile.objects.all().filter(profileVisible=True).filter(user__is_active=True)
    users = applyFilters(request, users)
    users = users.distinct()
    usersCounter = len(users)   

    return TemplateResponse(request, 'platforms.html', {'platforms': platforms,
                                                        'counter': counter,
                                                        'totalCount': totalCount,
                                                        'platformsCounter': counterPlatforms,
                                                        'resourcesCounter': resourcesCounter,
                                                        'trainingResourcesCounter': trainingResourcesCounter,
                                                        'projectsCounter': projectsCounter,
                                                        'organisationsCounter': organisationsCounter,
                                                        'usersCounter': usersCounter,
                                                        'countriesWithContent': countriesWithContent,
                                                        'geographicExtendWithContent': geographicExtendsWithContent,
                                                        'filters': filters,
                                                        'isSearchPage': True,
                                                        'show_search_bar': False})


def platformsAutocompleteSearch(request):
    if request.GET.get('q'):
        text = request.GET['q']
        platforms = getPlatformsAutocomplete(text)
        platforms = list(platforms)
        return JsonResponse(platforms, safe=False)
    else:
        return HttpResponse("No cookies")


def getPlatformsAutocomplete(text):
    platforms = Platform.objects.filter(name__icontains=text).values_list('id', 'name').distinct()
    report = []
    for platform in platforms:
        report.append({"type": "platform", "id": platform[0], "text": platform[1]})
    return report


def setImages(request, form):
    images = {}
    for key, value in request.FILES.items():
        x = form.cleaned_data.get('x' + key)
        y = form.cleaned_data.get('y' + key)
        w = form.cleaned_data.get('width' + key)
        h = form.cleaned_data.get('height' + key)
        image = Image.open(value)
        image = image.crop((x, y, w+x, h+y))
        if(key == 'profileImage'):
            finalsize = (1100, 400)
        else:
            finalsize = (600, 400)
        image = image.resize(finalsize, Image.LANCZOS)
        imagePath = getImagePath(value.name)
        image.save('media/'+imagePath)
        images[key] = imagePath
    print(images)
    print("-00.")
    return(images)


def getImagePath(imageName):
    _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
    random_num = random.randint(0, 1000)
    image_path = "images/" + _datetime + '_' + str(random_num) + '_' + imageName
    return image_path

def sendPlatformEmail(pk, user):
    platform2 = get_object_or_404(Platform, id=pk)
    subject = '[EU-CITIZEN.SCIENCE] Your platform "%s" has been submitted' % platform2.name
    print(subject)
    message = render_to_string('emails/new_platform.html', {
        'username': user.name,
        'domain': settings.HOST,
        'platformname': platform2.name,
        'platformid': pk})
    # to = [user.email]
    to = copy.copy(settings.EMAIL_RECIPIENT_LIST)
    to.append(user.email)
    bcc = copy.copy(settings.EMAIL_RECIPIENT_LIST)
    email = EmailMessage(subject, message, to=to, bcc=bcc)
    email.content_subtype = "html"
    email.send()
    print(message)   

def applyFilters(request, queryset):
    if queryset.model == Project:
        if request.GET.get('keywords'):
            queryset = queryset.filter(
                Q(name__icontains=request.GET['keywords']) |
                Q(keywords__keyword__icontains=request.GET['keywords'])).distinct()
            queryset = queryset.filter(approved=True)

    if queryset.model == Resource:
        if request.GET.get('keywords'):
            queryset = queryset.filter(
                Q(name__icontains=request.GET['keywords']) |
                Q(keywords__keyword__icontains=request.GET['keywords'])).distinct()
            queryset = queryset.filter(approved=True)

    if queryset.model == Profile:
        if request.GET.get('keywords'):
            keywords = request.GET.get('keywords')
            queryset = queryset.filter(
                Q(user__name__icontains=keywords) |
                Q(interestAreas__interestArea__icontains=keywords) |
                Q(bio__icontains=keywords)).distinct()
            
    if queryset.model == Organisation:
        if request.GET.get('keywords'):
            queryset = queryset.filter(
                Q(name__icontains=request.GET['keywords'])).distinct()
            
    if queryset.model == Platform:
        if request.GET.get('keywords'):
            keywords = request.GET.get('keywords')
            queryset = queryset.filter(name__icontains=keywords).distinct()  
        if request.GET.get('country'):
            queryset = queryset.filter(countries__icontains=request.GET['country']).distinct()
        if request.GET.get('geographicExtend'):
            queryset = queryset.filter(geographicExtend__icontains=request.GET['geographicExtend']).distinct()
            
    return queryset

def setFilters(request, filters):
    if request.GET.get('keywords'):
        filters['keywords'] = request.GET['keywords']
    if request.GET.get('country'):
        filters['country'] = request.GET['country']
    if request.GET.get('geographicExtend'):
        filters['geographicExtend'] = request.GET['geographicExtend']
    if request.GET.get('orderby'):
        filters['orderby'] = request.GET['orderby']    
    return filters