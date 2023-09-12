from __future__ import unicode_literals
from django.http import HttpResponse
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from itertools import chain
from . import forms
from . import models
from .models import Profile
from projects.models import Project, FollowedProjects, ProjectPermission, ApprovedProjects, UnApprovedProjects, Stats
from resources.models import Resource, BookmarkedResources, ResourcePermission, ApprovedResources, UnApprovedResources
from organisations.models import Organisation, OrganisationPermission
from platforms.models import Platform
from events.models import Event
from django.db.models.functions import Concat
from django.db.models import Value
from django.core.paginator import Paginator
import pprint
from django.db.models.functions import Lower


class ShowProfile(LoginRequiredMixin, generic.TemplateView):
    template_name = "profiles/show_profile.html"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        if slug:
            profile = get_object_or_404(models.Profile, slug=slug)
            user = profile.user
            if user.profile.profileVisible is True:
                kwargs["show_user"] = user

        else:
            user = self.request.user
            kwargs["show_user"] = user

        if user == self.request.user:
            kwargs["editable"] = True

        return super().get(request, *args, **kwargs)


class EditProfile(LoginRequiredMixin, generic.TemplateView):
    template_name = "profiles/edit_profile.html"
    http_method_names = ["get", "post"]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if "user_form" not in kwargs:
            kwargs["user_form"] = forms.UserForm(instance=user)
        if "profile_form" not in kwargs:
            kwargs["profile_form"] = forms.ProfileForm(
                    instance=user.profile,
                    initial={
                        'interestAreas': user.profile.interestAreas.all(),
                        'country': user.profile.country})
        kwargs["show_user"] = user
        if user == self.request.user:
            kwargs["editable"] = True

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print(request.POST)
        request.POST = request.POST.copy()
        request.POST = updateInterestAreas(request.POST)
        print(request.POST)

        user = self.request.user
        user_form = forms.UserForm(request.POST, instance=user)
        profile_form = forms.ProfileForm(
            request.POST, request.FILES, instance=user.profile
        )
        if not (user_form.is_valid() and profile_form.is_valid()):
            messages.error(
                request,
                "There was a problem with the form. " "Please check the details.",
            )
            user_form = forms.UserForm(instance=user)
            profile_form = forms.ProfileForm(instance=user.profile)
            return super().get(request, user_form=user_form, profile_form=profile_form)
        # Both forms are fine. Time to save!
        user_form.save()
        profile_form.save(request)
        messages.success(request, "Profile details saved!")
        return redirect("profiles:show_self")


class PrivacyCenter(LoginRequiredMixin, generic.TemplateView):
    template_name = "profiles/privacy_center.html"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):

        user = self.request.user
        if "user_form" not in kwargs:
            kwargs["user_form"] = forms.UserForm(instance=user)
        if "profile_form" not in kwargs:
            kwargs["profile_form"] = forms.ProfileForm(
                    instance=user.profile,
                    initial={
                        'interestAreas': user.profile.interestAreas.all(),
                        'country': user.profile.country})
        if user == self.request.user:
            kwargs["editable"] = True

        kwargs["show_user"] = user
        return super().get(request, *args, **kwargs)


class Submissions(generic.TemplateView):
    template_name = "profiles/submissions.html"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        if slug:
            profile = get_object_or_404(models.Profile, slug=slug)
            user = profile.user
        else:
            user = self.request.user
        projectsSubmitted = Project.objects.all().filter(creator=user).order_by('-dateUpdated')
        resourcesSubmitted = Resource.objects.all().filter(creator=user).filter(isTrainingResource=False)
        trainingsSubmitted = Resource.objects.all().filter(creator=user).filter(isTrainingResource=True)
        organisationsSubmitted = Organisation.objects.all().filter(creator=user)
        platformsSubmitted = Platform.objects.all().filter(creator=user)
        eventsSubmitted = Event.objects.all().filter(creator=user)
        kwargs["show_user"] = user
        kwargs["projects_submitted"] = projectsSubmitted
        kwargs["resources_submitted"] = resourcesSubmitted
        kwargs["trainings_submitted"] = trainingsSubmitted
        kwargs["organisations_submitted"] = organisationsSubmitted
        kwargs["platforms_submitted"] = platformsSubmitted
        kwargs["event_submitted"] = eventsSubmitted
        if user == self.request.user:
            kwargs["editable"] = True
        return super().get(request, *args, **kwargs)


class Bookmarks(LoginRequiredMixin, generic.TemplateView):
    template_name = "profiles/bookmarks.html"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        kwargs["show_user"] = user
        followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id', flat=True)
        projects = Project.objects.filter(id__in=followedProjects)
        bookmarkedResources = BookmarkedResources.objects.all().filter(
                user_id=user.id).values_list('resource_id', flat=True)
        resources = Resource.objects.filter(id__in=bookmarkedResources).filter(isTrainingResource=False)
        training = Resource.objects.filter(id__in=bookmarkedResources).filter(isTrainingResource=True)
        if user == self.request.user:
            kwargs["editable"] = True
        kwargs["projects_followed"] = projects
        kwargs["resources_followed"] = resources
        kwargs["trainings_followed"] = training

        return super().get(request, *args, **kwargs)
    
class MyStats(generic.TemplateView):
    template_name = "profiles/my_stats.html"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        if slug:
            profile = get_object_or_404(models.Profile, slug=slug)
            user = profile.user
        else:
            user = self.request.user
        projectsSubmitted = Project.objects.all().filter(creator=user).order_by('-dateUpdated')
        kwargs["show_user"] = user
        kwargs["projects_submitted"] = projectsSubmitted
        if user == self.request.user:
            kwargs["editable"] = True
        return super().get(request, *args, **kwargs)


class UsersSearch(generic.TemplateView):
    template_name = "profiles/usersSearch.html"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        users = Profile.objects.all().filter(profileVisible=True).filter(user__is_active=True).order_by('-user__last_login')
        filters = {'keywords': ''}
        # TODO: Add surname (needs to be added algo in the autocomplete search
        if request.GET.get('keywords'):
            users = users.filter(
                Q(user__name__icontains=request.GET['keywords']) |
                Q(interestAreas__interestArea__icontains=request.GET['keywords'])).distinct()
            filters['keywords'] = request.GET['keywords']

        counter = len(users)

        paginator = Paginator(users, 42)
        page = request.GET.get('page', 1)
        users = paginator.get_page(page)

        kwargs["users"] = users
        kwargs["isSearchPage"] = True
        kwargs["counter"] = counter
        kwargs["filters"] = filters
        return super().get(request, *args, **kwargs)
    
def userSearch(request):
    template_name = "profiles/usersSearch.html"
    users = Profile.objects.filter(profileVisible=True, user__is_active=True).order_by('-user__last_login')
    totalCount = len(Profile.objects.all())
    interestAreasWithContent = models.InterestArea.objects.filter(profile__in=users).order_by(Lower('interestArea')).distinct()
    organisationsWithContent = Profile.objects.all().filter(profileVisible=True).filter(user__is_active=True).values_list('organisation', flat=True).distinct()
    organisationsWithContent = Organisation.objects.filter(id__in=organisationsWithContent).order_by('name')
    countriesWithContent = Profile.objects.all().filter(profileVisible=True).filter(user__is_active=True).values_list('country', flat=True).distinct()
    filters = {'keywords': '', 'country': '', 'interestAreas': '', 'organisation': ''}
    users = applyFilters(request, users)
    filters = setFilters(request, filters)
    users = users.distinct()

    # Ordering
    if request.GET.get('orderby'):
        if(request.GET.get('orderby') == 'name'):
            users = users.order_by('surname')    
        else:
            users = users.order_by('-user__last_login')
        filters['orderby'] = request.GET['orderby']

    counter = len(users)
    usersCounter = len(users)

    paginator = Paginator(users, 42)
    page = request.GET.get('page', 1)
    users = paginator.get_page(page)

    #To count
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

    #For platforms count
    platforms = Platform.objects.all()
    platforms = applyFilters(request, platforms)
    platforms = platforms.distinct()
    platformsCounter = len(platforms)

    context = {
        'users': users,
        'isSearchPage': True,
        'counter': counter,
        'totalCount': totalCount,
        'usersCounter': usersCounter,
        'resourcesCounter': resourcesCounter,
        'trainingResourcesCounter': trainingResourcesCounter,
        'projectsCounter': projectsCounter,
        'organisationsCounter': organisationsCounter,
        'platformsCounter': platformsCounter,
        'interestAreas': interestAreasWithContent,
        'organisations': organisationsWithContent,
        'countriesWithContent': countriesWithContent,
        'filters': filters
    }
    return render(request, template_name, context)



def projects(request):
    user = request.user
    projectsCreated = Project.objects.all().filter(creator=user)
    projectsWithPermission = getProjectsWithPermission(user)
    projectsWithPermission = Project.objects.all().filter(id__in=projectsWithPermission)
    projects = chain(projectsCreated, projectsWithPermission)
    approvedProjects = ApprovedProjects.objects.all().values_list('project_id', flat=True)
    unApprovedProjects = UnApprovedProjects.objects.all().values_list('project_id', flat=True)
    return render(request, 'profiles/my_projects.html', {
        'show_user': user,
        'projects': projects,
        'approvedProjects': approvedProjects,
        'unApprovedProjects': unApprovedProjects})


def resources(request):
    user = request.user
    resourcesCreated = Resource.objects.all().filter(creator=user)
    resourcesWithPermission = getResourcesWithPermission(user)
    resourcesWithPermission = Resource.objects.all().filter(id__in=resourcesWithPermission)
    resources = chain(resourcesCreated, resourcesWithPermission)
    approvedResources = ApprovedResources.objects.all().values_list('resource_id', flat=True)
    unApprovedResources = UnApprovedResources.objects.all().values_list('resource_id', flat=True)
    return render(request, 'profiles/my_resources.html', {
        'show_user': user,
        'resources': resources,
        'approvedResources': approvedResources,
        'unApprovedResources': unApprovedResources})


def followedProjects(request):
    user = request.user
    followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id', flat=True)
    projects = Project.objects.filter(id__in=followedProjects)
    projects = projects.filter(~Q(hidden=True))
    return render(request, 'profiles/followed_projects.html', {
        'show_user': user,
        'projects': projects,
        'followedProjects': followedProjects})


def getProjectsWithPermission(user):
    projects = list(ProjectPermission.objects.all().filter(user_id=user).values_list('project', flat=True))
    return projects


def getResourcesWithPermission(user):
    resources = list(ResourcePermission.objects.all().filter(user_id=user).values_list('resource', flat=True))
    return resources


def organisations(request):
    user = request.user
    organisationsCreated = Organisation.objects.all().filter(creator=user)
    organisationsWithPermission = getOrganisationsWithPermission(user)
    organisationsWithPermission = Organisation.objects.all().filter(id__in=organisationsWithPermission)
    organisations = chain(organisationsCreated, organisationsWithPermission)
    return render(request, 'profiles/my_organisations.html', {'show_user': user, 'organisations': organisations})


def getOrganisationsWithPermission(user):
    organisations = list(
            OrganisationPermission.objects.all().filter(user_id=user).values_list('organisation', flat=True))
    return organisations


def updatePrivacy(request):
    user = request.user
    if 'subscribedtoDigest' in request.POST:
        user.profile.digest = (request.POST['subscribedtoDigest']).capitalize()
    if 'profileVisible' in request.POST:
        user.profile.profileVisible = (request.POST['profileVisible']).capitalize()
    if 'contentVisible' in request.POST:
        user.profile.contentVisible = (request.POST['contentVisible']).capitalize()

    user.profile.save()
    print(user.profile.digest)
    return JsonResponse("0", safe=False)


def updateInterestAreas(dictio):
    interestAreas = dictio.pop('interestAreas', None)
    if(interestAreas):
        for ia in interestAreas:
            if not ia.isdecimal():
                # This is a new interestArea
                models.InterestArea.objects.get_or_create(interestArea=ia)
                interestArea_id = models.InterestArea.objects.get(interestArea=ia).id
                dictio.update({'interestAreas': interestArea_id})
            else:
                # This keyword is already in the database
                dictio.update({'interestAreas': ia})
    return dictio


def usersAutocompleteSearch(request):
    if request.GET.get('q'):
        text = request.GET['q']
        users = getProfilesAutocomplete(text)
        users = list(users)
        return JsonResponse(users, safe=False)
    else:
        return HttpResponse("No cookies")


"""def getProfilesAutocomplete(text):
    profiles = models.Profile.objects.all().filter(
            Q(surname__icontains=text) | Q(user__name__icontains=text)).filter(profileVisible=True).annotate(
                    fullname=Concat('user__name', Value(' '), 'surname')).values_list('user__id', 'fullname', 'slug')
    interestAreas = models.InterestArea.objects.filter(
            interestArea__icontains=text).values_list('interestArea', flat=True).distinct()
    report = []
    for profile in profiles:
        report.append({"type": "profile", "id": profile[0], "text": profile[1], "slug": profile[2]})
    for interestArea in interestAreas:
        numberElements = models.Profile.objects.filter(
                profileVisible=True).filter(Q(interestAreas__interestArea__icontains=interestArea)).count()
        report.append({"type": "profileInterestArea", "text": interestArea, "numberElements": numberElements})
    return report """

def getProfilesAutocomplete(text):
    profiles = models.Profile.objects.all().filter(
        Q(surname__icontains=text) | Q(user__name__icontains=text)
    ).filter(profileVisible=True).annotate(
        fullname=Concat('user__name', Value(' '), 'surname')
    ).values('user__id', 'fullname', 'slug')

    interestAreas = models.InterestArea.objects.filter(interestArea__icontains=text).values_list('interestArea', flat=True).distinct()

    report = []
    for profile in profiles:
        report.append({
            "type": "profile",
            "id": str(profile['user__id']),
            "text": profile['fullname'],
            "slug": profile['slug']
        })

    for interestArea in interestAreas:
        numberElements = models.Profile.objects.filter(profileVisible=True).filter(interestAreas__interestArea__icontains=interestArea).count()
        report.append({
            "type": "profileInterestArea",
            "text": interestArea,
            "numberElements": numberElements
        })

    return report

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
            
    if queryset.model == Organisation:
        if request.GET.get('keywords'):
            queryset = queryset.filter(
                Q(name__icontains=request.GET['keywords'])).distinct()
            
    if queryset.model == Platform:
        if request.GET.get('keywords'):
            keywords = request.GET.get('keywords')
            queryset = queryset.filter(name__icontains=keywords).distinct()  
        
    if queryset.model == Profile:
        if request.GET.get('keywords'):
            keywords = request.GET.get('keywords')
            queryset = queryset.filter(
                Q(user__name__icontains=keywords) |
                Q(interestAreas__interestArea__icontains=keywords) |
                Q(bio__icontains=keywords)).distinct()
        if request.GET.get('country'):
            queryset = queryset.filter(country=request.GET['country'])
        if request.GET.get('interestAreas'):
            queryset = queryset.filter(interestAreas__interestArea__icontains=request.GET['interestAreas'])
        if request.GET.get('organisation'):
            organisation_name = request.GET['organisation']
            organisation = Organisation.objects.get(name=organisation_name)
            queryset = queryset.filter(organisation=organisation)
            
    return queryset

def setFilters(request, filters):
    if request.GET.get('keywords'):
        filters['keywords'] = request.GET['keywords']
    if request.GET.get('country'):
        filters['country'] = request.GET['country']
    if request.GET.get('interestAreas'):
        filters['interestAreas'] = request.GET['interestAreas']
    if request.GET.get('organisation'):
        filters['organisation'] = request.GET['organisation']
    if request.GET.get('orderby'):
        filters['orderby'] = request.GET['orderby']    
    return filters
