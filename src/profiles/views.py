from __future__ import unicode_literals
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from itertools import chain
from . import forms
from . import models
from projects.models import Project, FollowedProjects, ProjectPermission, ApprovedProjects, UnApprovedProjects
from resources.models import Resource, BookmarkedResources, ResourcePermission, ApprovedResources, UnApprovedResources
from organisations.models import Organisation, OrganisationPermission
from events.models import Event
from django.db.models.functions import Concat
from django.db.models import Value


class ShowProfile(LoginRequiredMixin, generic.TemplateView):
    template_name = "profiles/show_profile.html"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        if slug:
            profile = get_object_or_404(models.Profile, slug=slug)
            user = profile.user
        else:
            user = self.request.user

        if user == self.request.user:
            kwargs["editable"] = True
        kwargs["show_user"] = user
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
        projectsSubmitted = Project.objects.all().filter(creator=user)
        resourcesSubmitted = Resource.objects.all().filter(creator=user).filter(isTrainingResource=False)
        trainingsSubmitted = Resource.objects.all().filter(creator=user).filter(isTrainingResource=True)
        organisationsSubmitted = Organisation.objects.all().filter(creator=user)
        eventsSubmitted = Event.objects.all().filter(creator=user)
        kwargs["show_user"] = user
        kwargs["projects_submitted"] = projectsSubmitted
        kwargs["resources_submitted"] = resourcesSubmitted
        kwargs["trainings_submitted"] = trainingsSubmitted
        kwargs["organisations_submitted"] = organisationsSubmitted
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


def savedResources(request):
    user = request.user
    savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id', flat=True)
    resources = Resource.objects.filter(id__in=savedResources)
    resources = resources.filter(~Q(hidden=True))
    return render(request, 'profiles/saved_resources.html', {
        'show_user': user,
        'resources': resources,
        'savedResources': savedResources})


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


def getProfilesAutocomplete(text):
    print("Profiles")
    profiles = models.Profile.objects.all().filter(
            Q(surname__icontains=text) | Q(user__name__icontains=text)).annotate(
                    fullname=Concat('user__name', Value(' '), 'surname')).values_list('user__id', 'fullname', 'slug')
    report = []
    print(profiles)
    for profile in profiles:
        report.append({"type": "profile", "id": profile[0], "text": profile[1], "slug": profile[2]})
    return report
