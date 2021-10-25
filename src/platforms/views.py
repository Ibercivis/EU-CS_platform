from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import formats
from django.shortcuts import get_object_or_404, redirect

from rest_framework import status

from datetime import datetime
from PIL import Image

from .forms import PlatformForm
from .models import Platform

import random


# Create your views here.


@login_required(login_url='/login')
def newPlatform(request):
    user = request.user
    platformForm = PlatformForm()

    return render(request, 'platform_form.html', {'form': platformForm, 'user': user})


@login_required(login_url='/login')
def editPlatform(request, pk):
    user = request.user
    platform = get_object_or_404(Platform, id=pk)

    if user != platform.creator and not user.is_staff:
        return redirect('../platforms', {})

    platformForm = PlatformForm(initial={
        'name': platform.name,
        'url': platform.url,
        'description': platform.description,
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
    print(request.POST)
    form = PlatformForm(request.POST, request.FILES)
    if form.is_valid():
        images = setImages(request, form)
        pk = form.save(request, images)
        if request.POST.get('Id').isnumeric():
            return JsonResponse({'Platform updated': 'OK', 'Id': pk}, status=status.HTTP_200_OK)
        else:
            # sendPlatformEmail()
            return JsonResponse({'Platform created': 'OK', 'Id': pk}, status=status.HTTP_200_OK)
    else:
        return JsonResponse(form.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


def platform(request, pk):
    platform = get_object_or_404(Platform, id=pk)
    return render(request, 'platform.html', {'platform': platform})


def platforms(request):
    platforms = Platform.objects.get_queryset()
    return render(request, 'platforms.html', {'platforms': platforms, 'isSearchPage': True})


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
        image = image.resize(finalsize, Image.ANTIALIAS)
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
