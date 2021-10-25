from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import formats
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from datetime import datetime
from .forms import OrganisationForm, OrganisationPermissionForm
from .models import Organisation, OrganisationType, OrganisationPermission
from projects.models import Project
from resources.models import Resource
from profiles.models import Profile
import copy
import random

User = get_user_model()


@login_required(login_url='/login')
def new_organisation(request):
    user = request.user

    form = OrganisationForm()
    if request.method == 'POST':
        form = OrganisationForm(request.POST, request.FILES)
        if form.is_valid():
            image_path = ''
            if(request.FILES.get('logo')):
                x = form.cleaned_data.get('x')
                y = form.cleaned_data.get('y')
                w = form.cleaned_data.get('width')
                h = form.cleaned_data.get('height')
                photo = request.FILES['logo']
                image = Image.open(photo)
                cropped_image = image.crop((x, y, w+x, h+y))
                resized_image = cropped_image.resize((600, 400), Image.ANTIALIAS)
                _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
                random_num = random.randint(0, 1000)
                image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photo.name
                resized_image.save(image_path)
                image_path_database = "images/" + _datetime + '_' + str(random_num) + '_' + photo.name
            organisation = form.save(request, image_path_database)
            messages.success(request, _('Organisation added correctly'))
            subject = 'New organisation submitted'
            message = render_to_string('emails/new_organisation.html', {})
            to = copy.copy(settings.EMAIL_RECIPIENT_LIST)
            to.append(request.user.email)
            email = EmailMessage(subject, message, to=to)
            email.content_subtype = "html"
            email.send()
            return redirect('/organisation/'+str(organisation.id), {})
        else:
            print(form.errors)

    return render(
            request,
            'organisation_form.html',
            {'form': form, 'user': user})


def organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
    user = request.user
    cooperatorsPK = getCooperators(pk)
    if user != organisation.creator and not user.is_staff and not (user.id in cooperatorsPK):
        editable = False
    else:
        editable = True
    mainProjects = Project.objects.all().filter(mainOrganisation__id=pk)
    associatedProjects = Project.objects.all().filter(organisation__id=pk)
    associatedProjects |= mainProjects
    associatedResources = Resource.objects.all().filter(organisation__id=pk).filter(isTrainingResource=False)
    associatedTrainingResources = Resource.objects.all().filter(organisation__id=pk).filter(isTrainingResource=True)
    members = Profile.objects.all().filter(organisation__id=pk)
    users = getOtherUsers(organisation.creator, members)
    cooperators = getCooperatorsEmail(pk)
    permissionForm = OrganisationPermissionForm(
            initial={'usersCollection': users, 'selectedUsers': cooperators})

    return render(request, 'organisation.html', {
        'organisation': organisation,
        'associatedProjects': associatedProjects,
        'cooperators': cooperatorsPK,
        'associatedResources': associatedResources,
        'associatedTrainingResources': associatedTrainingResources,
        'members': members,
        'permissionForm': permissionForm,
        'editable': editable,
        'isSearchPage': True})


def edit_organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
    user = request.user
    cooperatorsPK = getCooperators(pk)
    if user != organisation.creator and not user.is_staff and not (user.id in cooperatorsPK):
        return redirect('../organisations', {})

    form = OrganisationForm(initial={
        'name': organisation.name,
        'url': organisation.url,
        'description': organisation.description,
        'orgType': organisation.orgType,
        'logo': organisation.logo,
        'withLogo': (True, False)[organisation.logo == ""],
        'contact_point': organisation.contactPoint,
        'contact_point_email': organisation.contactPointEmail,
        'latitude': organisation.latitude,
        'longitude': organisation.longitude
    })

    if request.method == 'POST':
        form = OrganisationForm(request.POST, request.FILES)
        if form.is_valid():
            image_path = ''
            if(request.FILES.get('logo')):
                x = form.cleaned_data.get('x')
                y = form.cleaned_data.get('y')
                w = form.cleaned_data.get('width')
                h = form.cleaned_data.get('height')
                photo = request.FILES['logo']
                image = Image.open(photo)
                cropped_image = image.crop((x, y, w+x, h+y))
                resized_image = cropped_image.resize((600, 400), Image.ANTIALIAS)
                _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
                random_num = random.randint(0, 1000)
                image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photo.name
                resized_image.save(image_path)
                image_path_database = "images/" + _datetime + '_' + str(random_num) + '_' + photo.name
            else:
                image_path_database = ''
            form.save(request, image_path_database)
            return redirect('/organisation/'+str(organisation.id), {})
        else:
            print(form.errors)

    return render(request, 'organisation_form.html', {
        'form': form,
        'organisation': organisation,
        'user': user})


def organisations(request):
    organisations = Organisation.objects.get_queryset().order_by('id')
    countriesWithContent = Organisation.objects.all().values_list('country', flat=True).distinct()
    orgTypes = OrganisationType.objects.all()
    filters = {'keywords': '', 'orgTypes': '', 'country': ''}
    if request.GET.get('keywords'):
        organisations = organisations.filter(
                Q(name__icontains=request.GET['keywords'])).distinct()
        filters['keywords'] = request.GET['keywords']
    if request.GET.get('country'):
        organisations = organisations.filter(country=request.GET['country'])
        filters['country'] = request.GET['country']
    if request.GET.get('orgTypes'):
        organisations = organisations.filter(orgType__type=request.GET['orgTypes'])
        filters['orgTypes'] = request.GET['orgTypes']

    counter = len(organisations)

    paginator = Paginator(organisations, 12)
    page = request.GET.get('page')
    organisations = paginator.get_page(page)

    return render(request, 'organisations.html', {
        'organisations': organisations,
        'counter': counter,
        'filters': filters,
        'countriesWithContent': countriesWithContent,
        'orgTypes': orgTypes,
        'isSearchPage': True})


def delete_organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
    user = request.user

    if user != organisation.creator and not user.is_staff:
        return redirect('../organisations', {})

    organisation.delete()

    return redirect('../organisations', {})


def organisationsAutocompleteSearch(request):
    if request.GET.get('q'):
        text = request.GET['q']
        organisations = getOrganisationAutocomplete(text)
        organisations = list(organisations)
        return JsonResponse(organisations, safe=False)
    else:
        return HttpResponse("No cookies")


def getOrganisationAutocomplete(text):
    organisations = Organisation.objects.filter(name__icontains=text).values_list('id', 'name').distinct()
    report = []
    for organisation in organisations:
        report.append({"type": "organisation", "id": organisation[0], "text": organisation[1]})
    return report


def preFilteredOrganisations(request):
    organisations = Organisation.objects.get_queryset().order_by('id')
    return applyFilters(request, organisations)


def applyFilters(request, organisations):
    if request.GET.get('country'):
        organisations = organisations.filter(country=request.GET['country'])
    if request.GET.get('orgType'):
        organisations = organisations.filter(orgType=request.GET['orgType'])
    return organisations


def getOtherUsers(creator, members):
    users = []
    for member in members:
        user = get_object_or_404(User, id=member.user_id)
        users.append(user.id)
    users = list(
            User.objects.filter(id__in=users).exclude(
                is_superuser=True).exclude(id=creator.id).values_list('name', 'email'))
    return users


def getCooperators(organisationID):
    users = list(
            OrganisationPermission.objects.all().filter(organisation_id=organisationID).values_list('user', flat=True))
    return users


def getCooperatorsEmail(organisationID):
    users = getCooperators(organisationID)
    cooperators = ""
    for user in users:
        userObj = get_object_or_404(User, id=user)
        cooperators += userObj.email + ", "
    return cooperators


def allowUserOrganisation(request):
    response = {}
    organisationID = request.POST.get("organisation_id")
    users = request.POST.get("users")
    organisation = get_object_or_404(Organisation, id=organisationID)
    if request.user != organisation.creator and not request.user.is_staff:
        # TODO return JsonResponse with error code
        return redirect('../organisations', {})

    # Delete all
    objs = OrganisationPermission.objects.all().filter(organisation_id=organisationID)
    if(objs):
        for obj in objs:
            obj.delete()

    # Insert all
    users = users.split(',')
    for user in users:
        fUser = User.objects.filter(email=user)[:1].get()
        organisationPermission = OrganisationPermission(organisation=organisation, user=fUser)
        organisationPermission.save()

    return JsonResponse(response, safe=False)


def saveImageWithPath(image, photoName):
    _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
    random_num = random.randint(0, 1000)
    image_path = "images/" + _datetime + '_' + str(random_num) + '_' + photoName
    image.save(image_path)
    return image_path
