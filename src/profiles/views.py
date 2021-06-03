from __future__ import unicode_literals
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from itertools import chain
from . import forms
from . import models
from projects.models import Project, FollowedProjects, ProjectPermission, ApprovedProjects, UnApprovedProjects
from resources.models import Resource, SavedResources, ResourcePermission, ApprovedResources, UnApprovedResources
from organisations.models import Organisation, OrganisationPermission
from ecsa.models import Delegate

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
        
        try:
            delegate = get_object_or_404(Delegate, user=user)
            organisationsMainDelegate = Organisation.objects.all().filter(mainDelegate=delegate)
            organisationsDelegate1 = Organisation.objects.all().filter(delegate1=delegate)
            organisationsDelegate2 = Organisation.objects.all().filter(delegate2=delegate)
            organisations = organisationsMainDelegate | organisationsDelegate1 | organisationsDelegate2
            kwargs["organisations"] = organisations
        except Exception:
            print("It's not a delegate")


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
            interestAreasList = list(user.profile.interestAreas.all().values_list('interestArea', flat=True))
            interestAreasList = ", ".join(interestAreasList)
            choices = interestAreasList
            kwargs["profile_form"] = forms.ProfileForm(instance=user.profile, initial={'choices': choices})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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

def projects(request):
    user = request.user
    projectsCreated = Project.objects.all().filter(creator=user)
    projectsWithPermission = getProjectsWithPermission(user)
    projectsWithPermission = Project.objects.all().filter(id__in=projectsWithPermission)
    projects = chain(projectsCreated, projectsWithPermission)
    approvedProjects = ApprovedProjects.objects.all().values_list('project_id',flat=True)
    unApprovedProjects = UnApprovedProjects.objects.all().values_list('project_id',flat=True)
    return render(request, 'profiles/my_projects.html', {'show_user': user, 'projects': projects, 'approvedProjects': approvedProjects, 'unApprovedProjects': unApprovedProjects})

def resources(request):
    user = request.user
    resourcesCreated = Resource.objects.all().filter(creator=user)
    resourcesWithPermission = getResourcesWithPermission(user)
    resourcesWithPermission = Resource.objects.all().filter(id__in=resourcesWithPermission)
    resources = chain(resourcesCreated, resourcesWithPermission)
    approvedResources = ApprovedResources.objects.all().values_list('resource_id',flat=True)
    unApprovedResources = UnApprovedResources.objects.all().values_list('resource_id',flat=True)
    return render(request, 'profiles/my_resources.html', {'show_user': user, 'resources': resources, 'approvedResources': approvedResources, 'unApprovedResources': unApprovedResources})

def followedProjects(request):
    user = request.user
    followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id', flat=True)
    projects = Project.objects.filter(id__in=followedProjects)
    projects = projects.filter(~Q(hidden=True))
    return render(request, 'profiles/followed_projects.html', {'show_user': user, 'projects': projects,'followedProjects': followedProjects })

def savedResources(request):
    user = request.user
    savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id', flat=True)
    resources= Resource.objects.filter(id__in=savedResources)
    resources = resources.filter(~Q(hidden=True))
    return render(request, 'profiles/saved_resources.html', {'show_user': user, 'resources': resources, 'savedResources': savedResources })

def getProjectsWithPermission(user):
    projects = list(ProjectPermission.objects.all().filter(user_id=user).values_list('project',flat=True))
    return projects

def getResourcesWithPermission(user):
    resources = list(ResourcePermission.objects.all().filter(user_id=user).values_list('resource',flat=True))
    return resources

def organisations(request):
    user = request.user
    organisationsCreated = Organisation.objects.all().filter(creator=user)
    organisationsWithPermission = getOrganisationsWithPermission(user)
    organisationsWithPermission = Organisation.objects.all().filter(id__in=organisationsWithPermission)
    organisations = chain(organisationsCreated, organisationsWithPermission)
    return render(request, 'profiles/my_organisations.html', {'show_user': user, 'organisations': organisations})

def getOrganisationsWithPermission(user):
    organisations = list(OrganisationPermission.objects.all().filter(user_id=user).values_list('organisation',flat=True))
    return organisations