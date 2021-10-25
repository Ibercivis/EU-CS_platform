from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.serializers import serialize
from django.utils import formats
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Avg, Count, Sum
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from datetime import datetime
from PIL import Image
from itertools import chain
from reviews.models import Review
from django_countries import countries
from .forms import ProjectForm, ProjectPermissionForm, ProjectTranslationForm, ProjectGeographicLocationForm
from .models import Project, Topic, ParticipationTask, Status, Keyword, ApprovedProjects, \
 FollowedProjects, FundingBody, CustomField, ProjectPermission, GeographicExtend, UnApprovedProjects, HasTag, DifficultyLevel
from organisations.models import Organisation
import copy
import csv
import json
import random
from rest_framework import status

User = get_user_model()


@login_required(login_url='/login')
def newProject(request):
    user = request.user
    form = ProjectForm()
    return render(request, 'project_form.html', {'form': form, 'user': user})


def saveProjectAjax(request):
    print(request.POST)
    request.POST = request.POST.copy()
    request.POST = updateKeywords(request.POST)
    request.POST = updateFundingBody(request.POST)
    form = ProjectForm(request.POST, request.FILES)
    if form.is_valid():
        images = setImages(request, form)
        pk = form.save(request, images, [], '')
        # We have pk after save and not projectID (this means is a new project)
        if (pk) and not request.POST.get('projectID').isnumeric():
            sendProjectEmail(pk, request.user)
        return JsonResponse({'Created': 'OK', 'Project': pk}, status=status.HTTP_200_OK)
    else:
        return JsonResponse(form.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


def sendProjectEmail(pk, user):
    project = get_object_or_404(Project, id=pk)
    subject = '[EU-CITIZEN.SCIENCE] Your project "%s" has been submitted' % project.name
    print(subject)
    message = render_to_string('emails/new_project.html', {
        'username': user.name,
        'domain': settings.HOST,
        'projectname': project.name,
        'projectid': pk})
    to = [user.email]
    bcc = copy.copy(settings.EMAIL_RECIPIENT_LIST)
    email = EmailMessage(subject, message, to=to, bcc=bcc)
    email.content_subtype = "html"
    email.send()
    print(message)


def updateKeywords(dictio):
    keywords = dictio.pop('keywords', None)
    if(keywords):
        for k in keywords:
            if not k.isdecimal():
                # This is a new keyword
                Keyword.objects.get_or_create(keyword=k)
                keyword_id = Keyword.objects.get(keyword=k).id
                dictio.update({'keywords': keyword_id})
            else:
                # This keyword is already in the database
                dictio.update({'keywords': k})
    return dictio


def updateFundingBody(dictio):
    fundingbodies = dictio.pop('funding_body', None)
    if(fundingbodies):
        for fb in fundingbodies:
            if not fb.isdecimal():
                # This is a new funding body
                FundingBody.objects.get_or_create(body=fb)
                fb_id = FundingBody.objects.get(body=fb).id
                dictio.update({'funding_body': fb_id})
            else:
                # This funding body is already in the database
                dictio.update({'funding_body': fb})
    return dictio


def getProjectTranslation(request):
    print(request.POST)
    project = get_object_or_404(Project, id=request.POST['projectId'])
    translation = project.translatedProject.filter(inLanguage=request.POST['language'])
    if not translation:
        return HttpResponse({}, status=status.HTTP_404_NOT_FOUND, content_type="application/json")
    else:
        translation_json = serializers.serialize('json', translation)
        return HttpResponse(translation_json, status=status.HTTP_200_OK, content_type="application/json")


def submitProjectTranslation(request):
    print(request.POST)
    form = ProjectTranslationForm(request.POST)
    if form.is_valid():
        form.save(request)
        return JsonResponse(
                {'UpdatedTranslation': 'OK', 'Project': request.POST['projectId']}, status=status.HTTP_200_OK)
    else:
        return JsonResponse(form.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


def editProject(request, pk):
    project = get_object_or_404(Project, id=pk)
    user = request.user
    cooperators = getCooperators(pk)
    if user != project.creator and not user.is_staff and not user.id in cooperators:
        return redirect('../projects', {})

    users = getOtherUsers(project.creator)
    cooperators = getCooperatorsEmail(pk)
    permissionForm = ProjectPermissionForm(initial={'usersCollection': users, 'selectedUsers': cooperators})

    start_datetime = None
    end_datetime = None

    if project.start_date:
        start_datetime = formats.date_format(project.start_date, 'Y-m-d')
    if project.end_date:
        end_datetime = formats.date_format(project.end_date, 'Y-m-d')

    form = ProjectForm(initial={
        'project_name': project.name,
        'url': project.url,
        'start_date': start_datetime,
        'projectlocality': project.projectlocality,
        'keywords': project.keywords.all,
        'end_date': end_datetime,
        'aim': project.aim,
        'description': project.description,
        'description_citizen_science_aspects': project.description_citizen_science_aspects,
        'status': project.status,
        'mainOrganisation': project.mainOrganisation,
        'organisation': project.organisation.all,
        'topic': project.topic.all,
        'participationTask': project.participationTask.all,
        'hasTag': project.hasTag.all,
        'difficultyLevel': project.difficultyLevel,
        'geographicextend': project.geographicextend.all,
        'projectGeographicLocation': project.projectGeographicLocation,
        'image1': project.image1,
        'image_credit1': project.imageCredit1,
        'withImage1': (True, False)[project.image1 == ""],
        'image2': project.image2,
        'image_credit2': project.imageCredit2,
        'withImage2': (True, False)[project.image2 == ""],
        'image3': project.image3,
        'image_credit3': project.imageCredit3,
        'withImage3': (True, False)[project.image3 == ""],
        'how_to_participate': project.howToParticipate,
        'equipment': project.equipment,
        'contact_person': project.author,
        'contact_person_email': project.author_email,
        'host': project.host,
        'funding_body': project.fundingBody.all,
        'doingAtHome': project.doingAtHome,
        'fundingBodySelected': project.fundingBody,
        'fundingProgram': project.fundingProgram,
        'originDatabase': project.originDatabase,
        'originUID': project.originUID,
        'originURL': project.originURL,
    })

    return render(request, 'project_form.html', {
        'form': form,
        'project': project,
        'user': user,
        'permissionForm': permissionForm})


def translateProject(request, pk):
    project = get_object_or_404(Project, id=pk)
    user = request.user

    form = ProjectTranslationForm()

    return render(request, 'translation_form.html', {
        'form': form,
        'project': project,
        'user': user})


def projects(request):
    projects = Project.objects.get_queryset()
    topics = Topic.objects.all()
    status = Status.objects.all()
    hasTag = HasTag.objects.all()
    difficultyLevel = DifficultyLevel.objects.all()
    participationTask = ParticipationTask.objects.all()
    countriesWithContent = 'ES'
    # approvedProjects = ApprovedProjects.objects.all().values_list('project_id', flat=True)
    # unApprovedProjects = UnApprovedProjects.objects.all().values_list('project_id', flat=True)
    filters = {
            'keywords': '',
            'topic': '',
            'status': 0,
            'host': '',
            'approvedCheck': '',
            'doingAtHome': '',
            'difficultyLevel': '',
            'hasTag': ''}

    projects = applyFilters(request, projects)
    filters = setFilters(request, filters)
    projects = projects.filter(~Q(hidden=True))

    # Ordering
    if request.GET.get('orderby'):
        orderBy = request.GET.get('orderby')
        if("featured" in orderBy):
            projectsTop = projects.filter(featured=True)
            projectsTopIds = list(projectsTop.values_list('id', flat=True))
            projects = projects.exclude(id__in=projectsTopIds)
            projects = list(projectsTop) + list(projects)
        else:
            reviews = Review.objects.filter(content_type=ContentType.objects.get(model="project"))
            reviews = reviews.values(
                    "object_pk",
                    "content_type").annotate(
                            avg_rating=Avg('rating')).order_by(orderBy).values_list('object_pk', flat=True)
            reviews = list(reviews)
            projectsVoted = []
            for r in reviews:
                proj = Project.objects.all().filter(id=r).first()
                if(proj):
                    if projects.filter(id=proj.id).exists():
                        projectsVoted.append(proj)

            projects = projects.exclude(id__in=reviews)
            if(orderBy == "avg_rating"):
                projects = list(projects) + list(projectsVoted)
            else:
                projects = list(projectsVoted) + list(projects)

        filters['orderby'] = request.GET['orderby']
    else:
        projects = projects.order_by('-dateUpdated')

    counter = len(projects)

    paginator = Paginator(projects, 16)
    page = request.GET.get('page')
    projects = paginator.get_page(page)

    return render(request, 'projects.html', {
        'projects': projects,
        'topics': topics,
        'countriesWithContent': countriesWithContent,
        'status': status,
        'filters': filters,
        'hasTag': hasTag,
        'difficultyLevel': difficultyLevel,
        'participationTask': participationTask,
        # 'approvedProjects': approvedProjects,
        # 'unApprovedProjects': unApprovedProjects,
        'counter': counter,
        'isSearchPage': True})


def project(request, pk):
    user = request.user
    project = get_object_or_404(Project, id=pk)
    users = getOtherUsers(project.creator)
    if project.projectGeographicLocation:
        form = ProjectGeographicLocationForm(initial={'projectGeographicLocation': project.projectGeographicLocation})
    else:
        form = None

    # Check if there is a translation
    hasTranslation = project.translatedProject.filter(inLanguage=request.LANGUAGE_CODE).exists()
    previous_page = request.META.get('HTTP_REFERER')
    if previous_page and 'review' in previous_page:
        # sendEmail
        subject = 'Your project has received a review'
        message = render_to_string(
                'emails/project_review.html',
                {"domain": settings.HOST, "name": project.name, "id": pk})
        to = copy.copy(settings.EMAIL_RECIPIENT_LIST)
        to.append(project.creator.email)
        email = EmailMessage(subject, message, to=to)
        email.content_subtype = "html"
        email.send()

    cooperators = getCooperatorsEmail(pk)
    unApprovedProjects = UnApprovedProjects.objects.all().values_list('project_id', flat=True)
    if (project.id in unApprovedProjects or project.hidden) and (user.is_anonymous or (user != project.creator and not user.is_staff and not user.id in getCooperators(pk))):
        return redirect('../projects', {})
    permissionForm = ProjectPermissionForm(initial={'usersCollection': users, 'selectedUsers': cooperators})
    followedProject = FollowedProjects.objects.all().filter(user_id=user.id, project_id=pk).exists()
    approvedProjects = ApprovedProjects.objects.all().values_list('project_id', flat=True)
    return render(request, 'project.html', {
        'project': project,
        'hasTranslation': hasTranslation,
        'followedProject': followedProject,
        'approvedProjects': approvedProjects,
        'unApprovedProjects': unApprovedProjects,
        'permissionForm': permissionForm,
        'cooperators': getCooperators(pk),
        'form': form,
        'isSearchPage': True})


def deleteProject(request, pk):
    obj = get_object_or_404(Project, id=pk)
    if request.user == obj.creator or request.user.is_staff or request.user.id in getCooperators(pk):
        obj.delete()
        reviews = Review.objects.filter(content_type=ContentType.objects.get(model="project"), object_pk=pk)
        for r in reviews:
            r.delete()
    return redirect('projects')


def setImages(request, form):
    print('setImages')
    images = []
    image1_path = saveImage(request, form, 'image1', '1')
    image2_path = saveImage(request, form, 'image2', '2')
    image3_path = saveImage(request, form, 'image3', '3')
    images.append(image1_path)
    images.append(image2_path)
    images.append(image3_path)
    print(images)
    return images


def saveImage(request, form, element, ref):
    image_path = ''
    filepath = request.FILES.get(element, False)
    withImage = form.cleaned_data.get('withImage' + ref)
    if (filepath):
        x = form.cleaned_data.get('x' + ref)
        y = form.cleaned_data.get('y' + ref)
        w = form.cleaned_data.get('width' + ref)
        h = form.cleaned_data.get('height' + ref)
        photo = request.FILES[element]
        image = Image.open(photo)
        cropped_image = image.crop((x, y, w+x, h+y))
        if(ref == '3'):
            finalSize = (1320, 400)
        else:
            finalSize = (600, 400)

        resized_image = cropped_image.resize(finalSize, Image.ANTIALIAS)

        if(cropped_image.width > image.width):
            size = (abs(int((finalSize[0]-(finalSize[0]/cropped_image.width*image.width))/2)), finalSize[1])
            whitebackground = Image.new(mode='RGBA', size=size, color=(255, 255, 255, 0))
            position = ((finalSize[0] - whitebackground.width), 0)
            resized_image.paste(whitebackground, position)
            position = (0, 0)
            resized_image.paste(whitebackground, position)
        if(cropped_image.height > image.height):
            size = (finalSize[0], abs(int((finalSize[1]-(finalSize[1]/cropped_image.height*image.height))/2)))
            whitebackground = Image.new(mode='RGBA', size=size, color=(255, 255, 255, 0))
            position = (0, (finalSize[1] - whitebackground.height))
            resized_image.paste(whitebackground, position)
            position = (0, 0)
            resized_image.paste(whitebackground, position)

        image_path = saveImageWithPath(resized_image, photo.name)
    elif withImage:
        image_path = '/'
    else:
        image_path = ''

    return image_path


def saveImageWithPath(image, photoName):
    _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
    random_num = random.randint(0, 1000)
    image_path = "images/" + _datetime + '_' + str(random_num) + '_' + photoName
    image.save("media/"+image_path)
    return image_path


def getOtherUsers(creator):
    users = list(User.objects.all().exclude(is_superuser=True).exclude(id=creator.id).values_list('name', 'email'))
    return users


def getCooperators(projectID):
    users = list(ProjectPermission.objects.all().filter(project_id=projectID).values_list('user', flat=True))
    return users


def getCooperatorsEmail(projectID):
    users = getCooperators(projectID)
    cooperators = ""
    for user in users:
        userObj = get_object_or_404(User, id=user)
        cooperators += userObj.email + ", "
    return cooperators


def projectsAutocompleteSearch(request):
    if request.GET.get('q'):
        text = request.GET['q']
        projects = getProjectsAutocomplete(text)
        projects = list(projects)
        return JsonResponse(projects, safe=False)
    else:
        return HttpResponse("No cookies")


def getProjectsAutocomplete(text):
    projects = Project.objects.filter(~Q(hidden=True)).filter(approved=True).filter(
            name__icontains=text).values_list('id', 'name').distinct()
    keywords = Keyword.objects.filter(keyword__icontains=text).values_list('keyword', flat=True).distinct()
    report = []
    for project in projects:
        report.append({"type": "project", "id": project[0], "text": project[1]})
    for keyword in keywords:
        numberElements = Project.objects.filter(Q(keywords__keyword__icontains=keyword)).count()
        report.append({"type": "keyword", "text": keyword, "numberElements": numberElements})
    return report


def preFilteredProjects(request):
    projects = Project.objects.get_queryset().order_by('id')
    return applyFilters(request, projects)


def applyFilters(request, projects):
    # approvedProjects = ApprovedProjects.objects.all().values_list('project_id', flat=True)
    if request.GET.get('keywords'):
        projects = projects.filter(
            Q(name__icontains=request.GET['keywords']) |
            Q(keywords__keyword__icontains=request.GET['keywords'])).distinct()

    if request.GET.get('topic'):
        projects = projects.filter(topic__topic=request.GET['topic'])

    if request.GET.get('status'):
        projects = projects.filter(status__status=request.GET['status'])

    if request.GET.get('doingAtHome'):
        projects = projects.filter(doingAtHome=request.GET['doingAtHome'])

    if request.GET.get('hasTag'):
        projects = projects.filter(hasTag__hasTag=request.GET['hasTag'])

    if request.GET.get('difficultyLevel'):
        projects = projects.filter(difficultyLevel__difficultyLevel=request.GET['difficultyLevel'])

    if request.GET.get('participationTask'):
        projects = projects.filter(participationTask__participationTask=request.GET['participationTask'])

    if request.GET.get('country'):
        projects = projects.filter(mainOrganisation__country=request.GET['country'])

    projects = projects.filter(approved=True)

    # if request.GET.get('approvedeck'):
    #    if request.GET['approvedCheck'] == 'On':
    #        projects = projects.filter(id__in=approvedProjects)
    #    if request.GET['approvedCheck'] == 'Off':
    #        projects = projects.exclude(id__in=approvedProjects)
    #    if request.GET['approvedCheck'] == 'All':
    #        projects = projects
    # else:
    #    projects = projects.filter(id__in=approvedProjects)

    return projects


def setFilters(request, filters):
    if request.GET.get('keywords'):
        filters['keywords'] = request.GET['keywords']
    if request.GET.get('topic'):
        filters['topic'] = request.GET['topic']
    if request.GET.get('status'):
        filters['status'] = request.GET['status']
    if request.GET.get('doingAtHome'):
        filters['doingAtHome'] = int(request.GET['doingAtHome'])
    if request.GET.get('approvedCheck'):
        filters['approvedCheck'] = request.GET['approvedCheck']
    if request.GET.get('hasTag'):
        filters['hasTag'] = request.GET['hasTag']
    if request.GET.get('difficultyLevel'):
        filters['difficultyLevel'] = request.GET['difficultyLevel']
    if request.GET.get('participationTask'):
        filters['participationTask'] = request.GET['participationTask']
    return filters


def clearFilters(request):
    return redirect('projects')


@staff_member_required()
def setApproved(request):
    response = {}
    id = request.POST.get("project_id")
    approved = request.POST.get("approved")
    setProjectApproved(id, approved)
    return JsonResponse(response, safe=False)


def setProjectApproved(id, approved):
    approved = False if approved in ['False', 'false', '0'] else True
    aProject = get_object_or_404(Project, id=id)
    if approved is True:
        # Insert
        ApprovedProjects.objects.get_or_create(project=aProject)
        aProject.approved = True
        aProject.moderated = True
        aProject.save()
        # sendEmail
        subject = 'Your project has been approved'
        message = render_to_string(
                'emails/approved_project.html',
                {
                    "domain": settings.HOST,
                    "name": aProject.name, "id": id})
        to = copy.copy(settings.EMAIL_RECIPIENT_LIST)
        to.append(aProject.creator.email)
        email = EmailMessage(subject, message, to=to)
        email.content_subtype = "html"
        email.send()
        # Delete from UnApprovedProjects
        try:
            obj = UnApprovedProjects.objects.get(project_id=id)
            obj.delete()
        except UnApprovedProjects.DoesNotExist:
            print("Does not exist this unapproved project")
    else:
        # Insert UnApprovedProjects
        UnApprovedProjects.objects.get_or_create(project=aProject)
        aProject.approved = False
        aProject.moderated = True
        aProject.save()

        # Delete it from approved projects
        try:
            obj = ApprovedProjects.objects.get(project_id=id)
            obj.delete()
        except ApprovedProjects.DoesNotExist:
            print("Does not exist this approved project")


@staff_member_required()
def setHidden(request):
    response = {}
    id = request.POST.get("project_id")
    hidden = request.POST.get("hidden")
    setProjectHidden(id, hidden)
    return JsonResponse(response, safe=False)


def setProjectHidden(id, hidden):
    project = get_object_or_404(Project, id=id)
    project.hidden = False if hidden in ['False','false','0'] else True
    project.save()


@staff_member_required()
def setFeatured(request):
    response = {}
    id = request.POST.get("project_id")
    featured = request.POST.get("featured")
    setProjectFeatured(id, featured)
    return JsonResponse(response, safe=False)


@staff_member_required()
def setProjectFeatured(id, featured):
    project = get_object_or_404(Project, id=id)
    project.featured = featured
    project.featured = False if featured in ['False', 'false', '0'] else True
    project.save()


def setFollowedProject(request):
    projectId = request.POST.get("projectId")
    bookmark = request.POST.get("bookmark")
    result = followProject(projectId, request.user.id, bookmark)
    if result == 'unfollowed':
        return JsonResponse({'id': projectId, 'bookmark': False})
    elif result.project.id == int(projectId):
        return JsonResponse({'id': projectId, 'bookmark': True})
    else:
        return JsonResponse({})


def followProject(projectId, userId, follow):
    follow = False if follow in ['False', 'false', '0'] else True
    fProject = get_object_or_404(Project, id=projectId)
    fUser = get_object_or_404(User, id=userId)
    if follow is True:
        # Insert
        followedProject = FollowedProjects.objects.get_or_create(project=fProject, user=fUser)
        # sendEmail
        subject = 'Your project has been followed'
        message = render_to_string('emails/followed_project.html', {
            "domain": settings.HOST,
            "name": fProject.name,
            "id": projectId})
        to = copy.copy(settings.EMAIL_RECIPIENT_LIST)
        to.append(fProject.creator.email)
        email = EmailMessage(subject, message, to=to)
        email.content_subtype = "html"
        email.send()
        return followedProject[0]
    else:
        # Delete
        try:
            obj = FollowedProjects.objects.get(project_id=projectId, user_id=userId)
            obj.delete()
            return 'unfollowed'
        except FollowedProjects.DoesNotExist:
            print("Does not exist this followed project")


def allowUser(request):
    response = {}
    projectId = request.POST.get("project_id")
    users = request.POST.get("users")
    project = get_object_or_404(Project, id=projectId)

    if request.user != project.creator and not request.user.is_staff:
        # TODO return JsonResponse with error code
        return redirect('../projects', {})

    # Delete all
    objs = ProjectPermission.objects.all().filter(project_id=projectId)
    if(objs):
        for obj in objs:
            obj.delete()

    # Insert all
    users = users.split(',')
    for user in users:
        fUser = User.objects.filter(email=user)[:1].get()
        projectPermission = ProjectPermission(project=project, user=fUser)
        projectPermission.save()

    return JsonResponse(response, safe=False)


def project_review(request, pk):
    return render(request, 'project_review.html', {'projectID': pk})


# Download all projects in a CSV file
def downloadProjects(request):
    projects = Project.objects.get_queryset()

    response = StreamingHttpResponse(
        streaming_content=(iter_items(projects, Buffer())),
        content_type='text/csv',
    )
    response['Content-Disposition'] = 'attachment; filename="projects.csv"'
    return response


def get_headers():
    return ['id', 'name', 'aim', 'description', 'keywords', 'status', 'start_date', 'end_date', 'topic', 'url',
     'host', 'howToParticipate', 'doingAtHome', 'equipment', 'fundingBody', 'fundingProgram', 'originDatabase', 'originURL', 'originUID']


def get_data(item):
    keywordsList = list(item.keywords.all().values_list('keyword', flat=True))
    topicList = list(item.topic.all().values_list('topic', flat=True))
    participationTaskList = list(item.participationTask.all().values_list('participationTask', flat=True))
    geographicextendList = list(item.geographicextend.all().values_list('geographicextend', flat=True))

    return {
        'id': item.id,
        'name': item.name,
        'aim': item.aim,
        'description': item.description,
        'keywords': keywordsList,
        'status': item.status,
        'start_date': item.start_date,
        'end_date': item.end_date,
        'topic': topicList,
        'participationTask': participationTaskList,
        'geographicextend': geographicextendList,
        'url': item.url,
        'projectlocality': item.projectlocality,
        'host': item.host,
        'howToParticipate': item.howToParticipate,
        'doingAtHome': item.doingAtHome,
        'equipment': item.equipment,
        'fundingBody': item.fundingBody,
        'fundingProgram': item.fundingProgram,
        'originDatabase': item.originDatabase,
        'originURL': item.originURL,
        'originUID': item.originUID,
    }


class Buffer(object):
    def write(self, value):
        return value


def iter_items(items, pseudo_buffer):
    writer = csv.DictWriter(pseudo_buffer, fieldnames=get_headers())
    yield ','.join(get_headers()) + '\r\n'

    for item in items:
        yield writer.writerow(get_data(item))


def projects_stats(request):

    return None
