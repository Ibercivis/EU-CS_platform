from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils import formats
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Avg
from datetime import datetime
from PIL import Image
from itertools import chain
from reviews.models import Review
from .forms import ProjectForm, CustomFieldForm, CustomFieldFormset, ProjectPermissionForm
from .models import Project, Topic, Status, Keyword, FeaturedProjects, FollowedProjects, FundingBody, CustomField, ProjectPermission,OriginDatabase
import json
import random

User = get_user_model()

def new_project(request):
    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)
    form = ProjectForm(initial={'choices': choices})
    user = request.user
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            images = []
            image1_path = saveImage(request, form, 'image1', '1')
            image2_path = saveImage(request, form, 'image2', '2')
            image3_path = saveImage(request, form, 'image3', '3')
            images.append(image1_path)
            images.append(image2_path)
            images.append(image3_path)
            form.save(request, images, [])

            messages.success(request, "Project added with success!")
            return redirect('/projects')
        else:
            print(form.errors)

    return render(request, 'new_project.html', {'form': form, 'user':user})

def saveImage(request, form, element, ref):
    image_path = ''
    filepath = request.FILES.get(element, False)
    if (filepath):
        x = form.cleaned_data.get('x' + ref)
        y = form.cleaned_data.get('y' + ref)
        w = form.cleaned_data.get('width' + ref)
        h = form.cleaned_data.get('height' + ref)
        photo = request.FILES[element]
        image = Image.open(photo)
        cropped_image = image.crop((x, y, w+x, h+y))
        if(ref == '3'):
            resized_image = cropped_image.resize((1100, 400), Image.ANTIALIAS)
        else:
            resized_image = cropped_image.resize((600, 400), Image.ANTIALIAS)
        _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
        random_num = random.randint(0, 1000)
        image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photo.name
        resized_image.save(image_path)

    return '/' + image_path

def projects(request):
    projects = Project.objects.get_queryset()
    featuredProjects = FeaturedProjects.objects.all().values_list('project_id',flat=True)
    user = request.user
    followedProjects = None
    followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id',flat=True)
    countriesWithContent = Project.objects.all().values_list('country',flat=True).distinct()

    topics = Topic.objects.all()
    status = Status.objects.all()
    filters = {'keywords': '', 'topic': '', 'status': 0, 'country': '', 'host': '', 'featuredCheck': '', 'doingAtHome': ''}

    if request.GET.get('keywords'):
        projects = projects.filter( Q(name__icontains = request.GET['keywords']) |
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
        filters['keywords'] = request.GET['keywords']

    if request.GET.get('topic'):
        projects = projects.filter(topic__topic = request.GET['topic'])
        filters['topic'] = request.GET['topic']

    if request.GET.get('status'):
        projects = projects.filter(status = request.GET['status'])
        filters['status'] = int(request.GET['status'])
    if request.GET.get('doingAtHome'):
        projects = projects.filter(doingAtHome = request.GET['doingAtHome'])
        filters['doingAtHome'] = int(request.GET['doingAtHome'])

    if request.GET.get('country'):
        projects = projects.filter(country = request.GET['country'])
        filters['country'] = request.GET['country']

    if request.GET.get('host'):
        projects = projects.filter( host__icontains = request.GET['host'])
        filters['host'] = request.GET['host']

    if request.GET.get('featuredCheck'):
        if request.GET['featuredCheck'] == 'On':
            projects = projects.filter(id__in=featuredProjects)
        if request.GET['featuredCheck'] == 'Off':
            projects = projects.exclude(id__in=featuredProjects)
        if request.GET['featuredCheck'] == 'All':
            projects = projects
        filters['featuredCheck'] = request.GET['featuredCheck']
    else:
        projects = projects.filter(id__in=featuredProjects)
    if not user.is_staff:
        projects = projects.filter(~Q(hidden=True))

    # Ordering
    if request.GET.get('orderby'):
        orderBy = request.GET.get('orderby')
        if("id" in orderBy):
            projects=projects.order_by(request.GET['orderby'])
        else:
            reviews = Review.objects.filter(content_type=ContentType.objects.get(model="project"))
            reviews = reviews.values("object_pk", "content_type").annotate(avg_rating=Avg('rating')).order_by(orderBy).values_list('object_pk',flat=True)
            reviews = list(reviews)
            projectsVoted = []
            for r in reviews:
                proj = get_object_or_404(Project, id=r)
                projectsVoted.append(proj)

            projects= projects.exclude(id__in=reviews)
            if(orderBy == "avg_rating"):
                projects = list(projects) + list(projectsVoted)
            else:
                projects = list(projectsVoted) + list(projects)

        filters['orderby']=request.GET['orderby']
    else:
        projects=projects.order_by('-id')


    paginator = Paginator(projects, 9)
    page = request.GET.get('page')
    projects = paginator.get_page(page)

    return render(request, 'projects.html', {'projects': projects, 'topics': topics, 'countriesWithContent': countriesWithContent,
    'status': status, 'filters': filters, 'featuredProjects': featuredProjects, 'followedProjects': followedProjects})


def project(request, pk):
    user = request.user
    project = get_object_or_404(Project, id=pk)
    users = getOtherUsers(project.creator)
    cooperators = getCooperatorsEmail(pk)
    permissionForm = ProjectPermissionForm(initial={'usersCollection':users, 'selectedUsers': cooperators})
    followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id',flat=True)
    featuredProjects = FeaturedProjects.objects.all().values_list('project_id',flat=True)
    return render(request, 'project.html', {'project':project, 'followedProjects':followedProjects,
    'featuredProjects':featuredProjects, 'permissionForm': permissionForm, 'cooperators': getCooperators(pk)})

def getOtherUsers(creator):
    users = list(User.objects.all().exclude(is_superuser=True).exclude(id=creator.id).values_list('email',flat=True))
    users = ", ".join(users)
    return users

def getCooperators(projectID):
    users = list(ProjectPermission.objects.all().filter(project_id=projectID).values_list('user',flat=True))
    return users

def getCooperatorsEmail(projectID):
    users = getCooperators(projectID)
    cooperators = ""
    for user in users:
        userObj = get_object_or_404(User, id=user)
        cooperators += userObj.email + ", "
    return cooperators

def editProject(request, pk):
    project = get_object_or_404(Project, id=pk)
    user = request.user
    cooperators = getCooperators(pk)
    if user != project.creator and not user.is_staff and not user.id in cooperators:
        return redirect('../projects', {})

    start_datetime = None
    end_datetime = None

    if project.start_date:
        start_datetime = formats.date_format(project.start_date, 'Y-m-d')
    if project.end_date:
        end_datetime = formats.date_format(project.end_date, 'Y-m-d')

    keywordsList = list(project.keywords.all().values_list('keyword', flat=True))
    keywordsList = ", ".join(keywordsList)

    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)

    fundingBody = list(FundingBody.objects.all().values_list('body',flat=True))
    fundingBody = ", ".join(fundingBody)

    originDatabase = list(OriginDatabase.objects.all().values_list('originDatabase',flat=True))
    originDatabase = ", ".join(originDatabase)

    form = ProjectForm(initial={
        'project_name':project.name,'url': project.url,'start_date': start_datetime,
        'end_date':end_datetime, 'aim': project.aim, 'description': project.description,
        'status': project.status, 'choices': choices, 'choicesSelected':keywordsList,
        'topic':project.topic.all, 'latitude': project.latitude, 'longitude': project.longitude,
        'image1': project.image1, 'image_credit1': project.imageCredit1, 'host': project.host,
        'image2': project.image2, 'image_credit2': project.imageCredit2,
        'image3': project.image3, 'image_credit3': project.imageCredit3,
        'how_to_participate': project.howToParticipate, 'equipment': project.equipment,
        'contact_person': project.author, 'contact_person_email': project.author_email,
        'funding_body': fundingBody, 'doingAtHome': project.doingAtHome, 'fundingBodySelected': project.fundingBody, 'fundingProgram': project.fundingProgram,
        'originDatabase': originDatabase,'originDatabaseSelected': project.originDatabase,
        'originUID' : project.originUID, 'originURL': project.originURL,
    })


    fields = list(project.customField.all().values())
    data = [{'title': l['title'], 'paragraph': l['paragraph']}
                    for l in fields]
    cField_formset = CustomFieldFormset(initial=data)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        cField_formset = CustomFieldFormset(request.POST)
        if form.is_valid() and cField_formset.is_valid():

            new_cFields = []
            for cField_form in cField_formset:
                title = cField_form.cleaned_data.get('title')
                paragraph = cField_form.cleaned_data.get('paragraph')
                if title and paragraph:
                    new_cFields.append(CustomField(title=title, paragraph=paragraph))
            images = []
            image1_path = saveImage(request, form, 'image1', '1')
            image2_path = saveImage(request, form, 'image2', '2')
            image3_path = saveImage(request, form, 'image3', '3')
            images.append(image1_path)
            images.append(image2_path)
            images.append(image3_path)
            form.save(request, images,[])
            return redirect('/project/'+ str(pk))
        else:
            print(form.errors)
    return render(request, 'editProject.html', {'form': form, 'project':project, 'user':user, 'cField_formset':cField_formset})


def deleteProject(request, pk):
    obj = get_object_or_404(Project, id=pk)
    obj.delete()
    return redirect('projects')

def text_autocomplete(request):
    projects = preFilteredProjects(request)
    if request.GET.get('q'):
        text = request.GET['q']
        projectsName = projects.filter( Q(name__icontains = text) ).distinct()
        projectsKey = projects.filter( Q(keywords__keyword__icontains = text) ).distinct()
        project_names = projectsName.values_list('name',flat=True).distinct()
        keywords = projectsKey.values_list('keywords__keyword',flat=False).distinct()
        keywords = Keyword.objects.filter(keyword__in = keywords).values_list('keyword',flat=True).distinct()
        report = chain(project_names, keywords)
        #report = getNamesKeywords(text)
        json = list(report)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")

def getNamesKeywords(text):
    project_names = Project.objects.filter(name__icontains=text).values_list('name',flat=True).distinct()
    keywords = Keyword.objects.filter(keyword__icontains=text).values_list('keyword',flat=True).distinct()
    report = chain(project_names, keywords)
    return report

def preFilteredProjects(request):
    projects = Project.objects.get_queryset().order_by('id')
    featuredProjects = FeaturedProjects.objects.all().values_list('project_id',flat=True)

    if request.GET.get('topic'):
        projects = projects.filter(topic__topic = request.GET['topic'])

    if request.GET.get('status') and int(request.GET.get('status')) > 0:
        projects = projects.filter(status = request.GET['status'])

    if request.GET.get('country'):
        projects = projects.filter(country = request.GET['country'])

    if request.GET.get('host'):
        projects = projects.filter( host__icontains = request.GET['host'])


    if request.GET.get('featuredCheck'):
        if request.GET['featuredCheck'] == 'On':
            projects = projects.filter(id__in=featuredProjects)
        if request.GET['featuredCheck'] == 'Off':
            projects = projects.exclude(id__in=featuredProjects)
        if request.GET['featuredCheck'] == 'All':
            projects = projects
    else:
        projects = projects.filter(id__in=featuredProjects)

    return projects

def host_autocomplete(request):
    if request.GET.get('q'):
        text = request.GET['q']
        data = Project.objects.filter(host__icontains=text).values_list('host',flat=True)
        json = list(data)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")

def clearFilters(request):
    return redirect ('projects')

def setFeatured(request):
    response = {}
    id = request.POST.get("project_id")

    #Delete
    try:
        obj = FeaturedProjects.objects.get(project_id=id)
        obj.delete()
    except FeaturedProjects.DoesNotExist:
        #Insert
        fProject = get_object_or_404(Project, id=id)
        featureProject = FeaturedProjects(project=fProject)
        featureProject.save()

    return JsonResponse(response, safe=False)

def setHidden(request):
    response = {}
    id = request.POST.get("project_id")
    hidden = request.POST.get("hidden")
    project = get_object_or_404(Project, id=id)
    project.hidden = False if hidden == 'false' else True
    project.save()
    return JsonResponse(response, safe=False)

def setFollowedProject(request):
    response = {}
    projectId = request.POST.get("project_id")
    userId = request.POST.get("user_id")
    #Delete
    try:
        obj = FollowedProjects.objects.get(project_id=projectId,user_id=userId)
        obj.delete()
    except FollowedProjects.DoesNotExist:
        #Insert
        fProject = get_object_or_404(Project, id=projectId)
        fUser = get_object_or_404(User, id=userId)
        followedProject = FollowedProjects(project=fProject, user=fUser)
        followedProject.save()

    return JsonResponse(response, safe=False)

def allowUser(request):
    response = {}
    projectId = request.POST.get("project_id")
    users = request.POST.get("users")

    #Delete all
    objs = ProjectPermission.objects.all().filter(project_id=projectId)
    if(objs):
        for obj in objs:
            obj.delete()

    #Insert all
    fProject = get_object_or_404(Project, id=projectId)
    users = users.split(',')
    for user in users:
        fUser = User.objects.filter(email=user)[:1].get()
        projectPermission = ProjectPermission(project=fProject, user=fUser)
        projectPermission.save()

    return JsonResponse(response, safe=False)

def project_review(request, pk):
    return render(request, 'project_review.html', {'projectID': pk})
