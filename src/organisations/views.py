from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.utils import formats
from django.db.models import Q
from datetime import datetime
from .forms import OrganisationForm
from .models import Organisation, OrganisationType
from projects.models import Project
from resources.models import Resource
from profiles.models import Profile
import random


@login_required(login_url='/login')
def new_organisation(request):
    user = request.user

    form = OrganisationForm()
    if request.method == 'POST':
        form = OrganisationForm(request.POST, request.FILES)
        if form.is_valid():
            image_path = ''
            if(request.FILES.get('logo', False)):
                photo = request.FILES['logo']
                image = Image.open(photo)
                _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
                random_num = random.randint(0, 1000)
                image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photo.name
                image.thumbnail((144,144))
                image.save(image_path)
            form.save(request, '/' + image_path)
            return redirect('../organisations', {})
        else:
            print(form.errors)

    return render(request, 'new_organisation.html', {'form': form, 'user':user})



def organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
    user = request.user
    if user != organisation.creator and not user.is_staff:
        editable = False
    else:
        editable = True
    mainProjects = Project.objects.all().filter(mainOrganisation__id=pk)
    associatedProjects = Project.objects.all().filter(organisation__id=pk)
    associatedProjects |=  mainProjects
    associatedResources = Resource.objects.all().filter(organisation__id=pk)
    members = Profile.objects.all().filter(organisation__id=pk)
    return render(request, 'organisation.html', {'organisation':organisation, 'associatedProjects': associatedProjects,
    'associatedResources': associatedResources, 'members': members, 'editable': editable, 'isSearchPage': True})


def edit_organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
    user = request.user

    if user != organisation.creator and not user.is_staff:
        return redirect('../organisations', {})

    form = OrganisationForm(initial={
        'name':organisation.name,'url': organisation.url, 'description': organisation.description,
        'orgType': organisation.orgType, 'logo': organisation.logo, 'contact_point': organisation.contactPoint,
        'contact_point_email': organisation.contactPointEmail, 'latitude': organisation.latitude, 'longitude': organisation.longitude
    })

    if request.method == 'POST':
        form = OrganisationForm(request.POST, request.FILES)
        if form.is_valid():
            image_path = ''
            if(request.FILES.get('logo', False)):
                photo = request.FILES['logo']
                image = Image.open(photo)
                _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
                random_num = random.randint(0, 1000)
                image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photo.name
                image.thumbnail((144,144))
                image.save(image_path)
                image_path = '/' + image_path
            form.save(request, image_path)
            return redirect('../organisations', {})
        else:
            print(form.errors)

    return render(request, 'edit_organisation.html', {'form': form, 'organisation':organisation, 'user':user,})

def organisations(request):
    organisations = Organisation.objects.get_queryset().order_by('id')
    countriesWithContent = Organisation.objects.all().values_list('country',flat=True).distinct()
    orgTypes = OrganisationType.objects.all()
    filters = {'keywords': '', 'orgType': '', 'country': ''}
    if request.GET.get('keywords'):
        organisations = organisations.filter( Q(name__icontains = request.GET['keywords'])).distinct()
        filters['keywords'] = request.GET['keywords']
    if request.GET.get('country'):
        organisations = organisations.filter(country = request.GET['country'])
        filters['country'] = request.GET['country']
    if request.GET.get('orgType'):
        organisations = organisations.filter(orgType = request.GET['orgType'])
        filters['orgType'] = request.GET['orgType']

    counter = len(organisations)

    paginator = Paginator(organisations, 12)
    page = request.GET.get('page')
    organisations = paginator.get_page(page)

    return render(request, 'organisations.html', {'organisations': organisations, 'counter': counter,
    'filters': filters, 'countriesWithContent': countriesWithContent, 'orgTypes': orgTypes,
    'isSearchPage': True})

def delete_organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
    user = request.user

    if user != organisation.creator and not user.is_staff:
        return redirect('../organisations', {})

    organisation.delete()

    return redirect('../organisations', {})

def organisations_autocomplete(request):
    organisations = preFilteredOrganisations(request)

    if request.GET.get('q'):
        text = request.GET['q']
        organisationsName = organisations.filter( Q(name__icontains = text) ).distinct()
        project_names = organisationsName.values_list('name',flat=True).distinct()
        json = list(project_names)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")

def preFilteredOrganisations(request):
    organisations = Organisation.objects.get_queryset().order_by('id')
    return applyFilters(request, organisations)

def applyFilters(request, organisations):
    if request.GET.get('country'):
        organisations = organisations.filter(country = request.GET['country'])
    if request.GET.get('orgType'):
        organisations = organisations.filter(orgType = request.GET['orgType'])
    return organisations
