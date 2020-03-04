from __future__ import unicode_literals
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from . import forms
from . import models
from projects.models import Project, FollowedProjects
from resources.models import Resource, SavedResources


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
    projects = Project.objects.all().filter(creator=user)

    return render(request, 'profiles/my_projects.html', {'show_user': user, 'projects': projects})

def resources(request):
    user = request.user
    resources = Resource.objects.all().filter(creator=user)

    return render(request, 'profiles/my_resources.html', {'show_user': user, 'resources': resources})

def followedProjects(request):
    user = request.user
    followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id', flat=True)    
    followedProjects = Project.objects.filter(id__in=followedProjects)
    return render(request, 'profiles/followed_projects.html', {'show_user': user, 'followedProjects': followedProjects})

def savedResources(request):
    user = request.user
    savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id', flat=True)
    savedResources = Resource.objects.filter(id__in=savedResources)
    return render(request, 'profiles/saved_resources.html', {'show_user': user, 'savedResources': savedResources})