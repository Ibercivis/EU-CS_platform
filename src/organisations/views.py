from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import formats
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from datetime import datetime
from .forms import OrganisationForm, OrganisationPermissionForm, NewEcsaOrganisationMembershipForm
from .models import Organisation, OrganisationType, OrganisationPermission, LEGAL_STATUS
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
            if(request.FILES.get('logo', False)):
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
            form.save(request, '/' + image_path)
            messages.success(request, _('Organisation added correctly'))
            subject = 'New organisation submitted'
            message = render_to_string('emails/new_organisation.html', {})
            to = copy.copy(settings.EMAIL_RECIPIENT_LIST)
            to.append(request.user.email)
            email = EmailMessage(subject, message, to=to)
            email.content_subtype = "html"
            email.send()
            return redirect('../organisations', {})
        else:
            print(form.errors)

    return render(request, 'new_organisation.html', {'form': form, 'user': user})



def organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
    if(organisation.legal_status != None):
        organisation.legal_status = LEGAL_STATUS[ organisation.legal_status][1]
    user = request.user
    cooperatorsPK = getCooperators(pk)
    if user != organisation.creator and not user.is_staff and not user.id in cooperatorsPK:
        editable = False
    else:
        editable = True
    mainProjects = Project.objects.all().filter(mainOrganisation__id=pk)
    associatedProjects = Project.objects.all().filter(organisation__id=pk)
    associatedProjects |=  mainProjects
    associatedResources = Resource.objects.all().filter(organisation__id=pk)
    members = Profile.objects.all().filter(organisation__id=pk)
    users = getOtherUsers(organisation.creator, members)
    cooperators = getCooperatorsEmail(pk)
    permissionForm = OrganisationPermissionForm(initial={'usersCollection':users, 'selectedUsers': cooperators})
    return render(request, 'organisation.html', {'organisation':organisation, 'associatedProjects': associatedProjects,'cooperators': cooperatorsPK,
    'associatedResources': associatedResources, 'members': members, 'permissionForm': permissionForm, 'editable': editable, 'isSearchPage': True, 'LEGAL_STATUS':LEGAL_STATUS})


def edit_organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
    user = request.user
    cooperatorsPK = getCooperators(pk)
    if user != organisation.creator and not user.is_staff and not user.id in cooperatorsPK:
        return redirect('../organisations', {})

    form = OrganisationForm(initial={
        'name':organisation.name,'url': organisation.url, 'description': organisation.description,
        'orgType': organisation.orgType, 'logo': organisation.logo, 'withLogo': (True, False)[organisation.logo == ""],
        'contact_point': organisation.contactPoint,'contact_point_email': organisation.contactPointEmail,
        'latitude': organisation.latitude, 'longitude': organisation.longitude
    })

    if request.method == 'POST':
        form = OrganisationForm(request.POST, request.FILES)
        if form.is_valid():
            image_path = ''
            withLogo = form.cleaned_data.get('withLogo')
            if(request.FILES.get('logo', False)):
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
                image_path = '/' + image_path
            elif withLogo:
                    image_path = '/'
            else:
                image_path = ''
            form.save(request, image_path)
            return redirect('../organisations', {})
        else:
            print(form.errors)

    return render(request, 'edit_organisation.html', {'form': form, 'organisation':organisation, 'user':user,})

def newEcsaOrganisationMembership(request, pk):
    form = NewEcsaOrganisationMembershipForm()
    if request.method == 'POST':
        form = NewEcsaOrganisationMembershipForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('ecsa_billing_email')
            newEcsaOrganisationMembershipEmail(email, request.user.name)
            form.save(request, pk)
            return redirect('/organisation/'+ str(pk))

    return render(request, 'new_ecsa_organisation_membership.html/', {'form': form, 'organisationID': pk})

def newEcsaOrganisationMembershipEmail(email, name):
    to_email = email
    subject = 'Thank you! - Become a member of ECSA'          
    message = render_to_string('accounts/emails/new_ecsa_individual_membership.html', { 'name': name, })
    email = EmailMessage(subject, message, to=[to_email], bcc=settings.EMAIL_ECSA_ADMIN)
    email.content_subtype = "html"
    email.send()


def dropOutECSAmembership(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)    
    organisation.ecsa_requested_join = False
    organisation.ecsa_member = False
    organisation.save()
    return redirect("/users/me/organisations")

def claimEcsaPaymentRevision(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)  
    organisation.ecsa_payment_revision = True
    organisation.save()
    #send email
    subject = 'ECSA membership payment revision'
    from_email = organisation.contactPointEmail
    message = "I want an ECSA membership payment revision"
    try:
        send_mail(subject, message, from_email, settings.EMAIL_CONTACT_RECIPIENT_LIST, html_message=message)
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
    return redirect("/users/me/organisations")

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

def getOtherUsers(creator, members):
    users = []
    for member in members:
        user = get_object_or_404(User, id=member.user_id)
        users.append(user.id)
    users = list(User.objects.filter(id__in=users).exclude(is_superuser=True).exclude(id=creator.id).values_list('name','email'))
    return users

def getCooperators(organisationID):
    users = list(OrganisationPermission.objects.all().filter(organisation_id=organisationID).values_list('user',flat=True))
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
        #TODO return JsonResponse with error code
        return redirect('../organisations', {})

    #Delete all
    objs = OrganisationPermission.objects.all().filter(organisation_id=organisationID)
    if(objs):
        for obj in objs:
            obj.delete()

    #Insert all
    users = users.split(',')
    for user in users:
        fUser = User.objects.filter(email=user)[:1].get()
        organisationPermission = OrganisationPermission(organisation=organisation, user=fUser)
        organisationPermission.save()

    return JsonResponse(response, safe=False)

def saveImageWithPath(image, photoName):
    _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
    random_num = random.randint(0, 1000)
    image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photoName
    image.save(image_path)
    image_path = '/' + image_path
    return image_path
