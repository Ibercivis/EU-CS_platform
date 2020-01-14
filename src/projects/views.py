from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from .forms import ProjectForm
from django.utils import timezone
from .models import Project, Category
from django.contrib.auth import get_user_model
import json
from django.utils.dateparse import parse_datetime
from datetime import datetime
from django.utils import formats
from django.contrib import messages


def new_project(request):
    form = ProjectForm()
    user = request.user
    if request.method == 'POST':
        form = ProjectForm(request.POST) 
        if form.is_valid():
            form.save(request)
            messages.success(request, "Project added with success!")
            return redirect('/projects')

    return render(request, 'new_project.html', {'form': form, 'user':user})

def projects(request):
    projects = Project.objects.all()

    return render(request, 'projects.html', {'projects':projects})


    