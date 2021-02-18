from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.utils import formats
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Avg
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from PIL import Image
from itertools import chain
from reviews.models import Review
from .forms import ProjectForm, CustomFieldFormset, ProjectPermissionForm
from .models import Project, Topic,ParticipationTask, Status, Keyword, ApprovedProjects, \
 FollowedProjects, FundingBody, CustomField, ProjectPermission, OriginDatabase, GeographicExtend, UnApprovedProjects
from organisations.models import Organisation
import csv
import json
import random

User = get_user_model()

@login_required(login_url='/login')
def new_project(request):
    user = request.user
    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)
    form = ProjectForm(initial={'choices': choices})
    if request.method == 'POST':
        mainOrganisationFixed = request.POST.get('mainOrganisation', False)
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            images = setImages(request, form)
            form.save(request, images, [],mainOrganisationFixed)
            messages.success(request, _('Project added correctly'))
            return redirect('/projects')
        else:
            print(form.errors)

    return render(request, 'new_project.html', {'form': form, 'user':user})


def projects(request):
    projects = Project.objects.get_queryset()
    approvedProjects = ApprovedProjects.objects.all().values_list('project_id',flat=True)
    unApprovedProjects = UnApprovedProjects.objects.all().values_list('project_id',flat=True)
    user = request.user
    followedProjects = None
    followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id',flat=True)
    countriesWithContent = Project.objects.all().values_list('country',flat=True).distinct()

    topics = Topic.objects.all()
    status = Status.objects.all()
    filters = {'keywords': '', 'topic': '', 'status': 0, 'country': '', 'host': '', 'approvedCheck': '', 'doingAtHome': ''}

    if request.GET.get('keywords'):
        projects = projects.filter( Q(name__icontains = request.GET['keywords']) |
                                    Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
        filters['keywords'] = request.GET['keywords']

    projects = applyFilters(request, projects)
    filters = setFilters(request, filters)

    projects = projects.filter(~Q(hidden=True))


    if not user.is_staff:
        projects = projects.exclude(id__in=unApprovedProjects)

    # Ordering
    if request.GET.get('orderby'):
        orderBy = request.GET.get('orderby')
        if("featured" in orderBy):
            projectsTop = projects.filter(featured=True)
            projectsTopIds = list(projectsTop.values_list('id',flat=True))
            projects = projects.exclude(id__in=projectsTopIds)
            projects = list(projectsTop) + list(projects)
        else:
            reviews = Review.objects.filter(content_type=ContentType.objects.get(model="project"))
            reviews = reviews.values("object_pk",
            "content_type").annotate(avg_rating=Avg('rating')).order_by(orderBy).values_list('object_pk',flat=True)
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

        filters['orderby']=request.GET['orderby']
    else:
        projects=projects.order_by('-dateUpdated')

    
    counter = len(projects)

    paginator = Paginator(projects, 12)
    page = request.GET.get('page')
    projects = paginator.get_page(page)

    return render(request, 'projects.html', {'projects': projects, 'topics': topics, 'countriesWithContent': countriesWithContent,
    'status': status, 'filters': filters, 'approvedProjects': approvedProjects, 'unApprovedProjects': unApprovedProjects,'followedProjects': followedProjects,
    'counter': counter, 'isSearchPage': True })


def project(request, pk):
    user = request.user
    project = get_object_or_404(Project, id=pk)
    users = getOtherUsers(project.creator)
    cooperators = getCooperatorsEmail(pk)
    unApprovedProjects = UnApprovedProjects.objects.all().values_list('project_id',flat=True)
    if (project.id in unApprovedProjects or project.hidden) and ( user.is_anonymous or (user != project.creator and not user.is_staff and not user.id in getCooperators(pk))):
        return redirect('../projects', {})
    permissionForm = ProjectPermissionForm(initial={'usersCollection':users, 'selectedUsers': cooperators})
    followedProjects = FollowedProjects.objects.all().filter(user_id=user.id).values_list('project_id',flat=True)
    approvedProjects = ApprovedProjects.objects.all().values_list('project_id',flat=True)    
    return render(request, 'project.html', {'project':project, 'followedProjects':followedProjects,
    'approvedProjects':approvedProjects, 'unApprovedProjects': unApprovedProjects,'permissionForm': permissionForm, 'cooperators': getCooperators(pk),
    'isSearchPage': True})


def editProject(request, pk):
    project = get_object_or_404(Project, id=pk)
    user = request.user
    cooperators = getCooperators(pk)
    if user != project.creator and not user.is_staff and not user.id in cooperators:
        return redirect('../projects', {})

    users = getOtherUsers(project.creator)
    cooperators = getCooperatorsEmail(pk)
    permissionForm = ProjectPermissionForm(initial={'usersCollection':users, 'selectedUsers': cooperators})

    start_datetime = None
    end_datetime = None

    if project.start_date:
        start_datetime = formats.date_format(project.start_date, 'Y-m-d')
    if project.end_date:
        end_datetime = formats.date_format(project.end_date, 'Y-m-d')

    choices = list(Keyword.objects.all().values_list('keyword',flat=True))
    choices = ", ".join(choices)

    fundingBody = list(FundingBody.objects.all().values_list('body',flat=True))
    fundingBody = ", ".join(fundingBody)

    originDatabase = list(OriginDatabase.objects.all().values_list('originDatabase',flat=True))
    originDatabase = ", ".join(originDatabase)

    form = ProjectForm(initial={
        'project_name':project.name,'url': project.url,'start_date': start_datetime, 'projectlocality': project.projectlocality,
        'end_date':end_datetime, 'aim': project.aim, 'description': project.description,
        'status': project.status, 'choices': choices, 'mainOrganisation': project.mainOrganisation,
        'organisation': project.organisation.all,
        'topic':project.topic.all, 'participationtask': project.participationtask.all, 'geographicextend': project.geographicextend.all,
        'latitude': project.latitude, 'longitude': project.longitude,
        'image1': project.image1, 'image_credit1': project.imageCredit1, 'withImage1': (True, False)[project.image1 == ""],
        'image2': project.image2, 'image_credit2': project.imageCredit2, 'withImage2': (True, False)[project.image2 == ""],
        'image3': project.image3, 'image_credit3': project.imageCredit3, 'withImage3': (True, False)[project.image3 == ""],
        'how_to_participate': project.howToParticipate, 'equipment': project.equipment,
        'contact_person': project.author, 'contact_person_email': project.author_email, 'host': project.host,
        'funding_body': fundingBody, 'doingAtHome': project.doingAtHome, 'fundingBodySelected': project.fundingBody, 'fundingProgram': project.fundingProgram,
        'originDatabase': originDatabase,'originDatabaseSelected': project.originDatabase,
        'originUID' : project.originUID, 'originURL': project.originURL,
    })


    fields = list(project.customField.all().values())
    data = [{'title': l['title'], 'paragraph': l['paragraph']}
                    for l in fields]
    cField_formset = CustomFieldFormset(initial=data)

    if request.method == 'POST':
        mainOrganisationFixed = request.POST.get('mainOrganisation', False)
        form = ProjectForm(request.POST, request.FILES)
        cField_formset = CustomFieldFormset(request.POST)
        if form.is_valid() and cField_formset.is_valid():
            new_cFields = []
            for cField_form in cField_formset:
                title = cField_form.cleaned_data.get('title')
                paragraph = cField_form.cleaned_data.get('paragraph')
                if title and paragraph:
                    new_cFields.append(CustomField(title=title, paragraph=paragraph))
            images = setImages(request, form)
            form.save(request, images,[],mainOrganisationFixed)
            return redirect('/project/'+ str(pk))
        else:
            print(form.errors)
    return render(request, 'editProject.html', {'form': form, 'project':project, 'user':user, 'cField_formset':cField_formset,
                'permissionForm': permissionForm})



def deleteProject(request, pk):
    obj = get_object_or_404(Project, id=pk)
    if request.user == obj.creator or request.user.is_staff or request.user.id in getCooperators(pk):
        obj.delete()
        reviews = Review.objects.filter(content_type=ContentType.objects.get(model="project"), object_pk=pk)
        for r in reviews:
            r.delete()
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
        json = list(report)
        return JsonResponse(json, safe=False)
    else:
        return HttpResponse("No cookies")


def setImages(request, form):
    images = []
    image1_path = saveImage(request, form, 'image1', '1')
    image2_path = saveImage(request, form, 'image2', '2')
    image3_path = saveImage(request, form, 'image3', '3')
    images.append(image1_path)
    images.append(image2_path)
    images.append(image3_path)
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
            finalSize = (1100, 400)
        else:
            finalSize = (600, 400)

        resized_image = cropped_image.resize(finalSize, Image.ANTIALIAS)

        if(cropped_image.width > image.width):
            size = (abs(int((finalSize[0]-(finalSize[0]/cropped_image.width*image.width))/2)), finalSize[1])
            whitebackground = Image.new(mode='RGBA',size=size,color=(255,255,255,0))
            position = ((finalSize[0] - whitebackground.width), 0)
            resized_image.paste(whitebackground, position)
            position = (0, 0)
            resized_image.paste(whitebackground, position)
        
        if(cropped_image.height > image.height):
            size = (finalSize[0], abs(int((finalSize[1]-(finalSize[1]/cropped_image.height*image.height))/2)))
            whitebackground = Image.new(mode='RGBA',size=size,color=(255,255,255,0))
            position = (0, (finalSize[1] - whitebackground.height))
            resized_image.paste(whitebackground, position)
            position = (0, 0)
            resized_image.paste(whitebackground, position)

        image_path = saveImageWithPath(resized_image, photo.name)
    elif withImage:
            image_path = '/'
    else:
        image_path = ''

    return  image_path

def saveImageWithPath(image, photoName):
    _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
    random_num = random.randint(0, 1000)
    image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photoName
    image.save(image_path)
    image_path = '/' + image_path
    return image_path

def getOtherUsers(creator):
    users = list(User.objects.all().exclude(is_superuser=True).exclude(id=creator.id).values_list('name','email'))
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

def getNamesKeywords(text):
    project_names = Project.objects.filter(name__icontains=text).values_list('name',flat=True).distinct()
    keywords = Keyword.objects.filter(keyword__icontains=text).values_list('keyword',flat=True).distinct()
    report = chain(project_names, keywords)
    return report

def preFilteredProjects(request):
    projects = Project.objects.get_queryset().order_by('id')
    return applyFilters(request, projects)

def applyFilters(request, projects):
    approvedProjects = ApprovedProjects.objects.all().values_list('project_id',flat=True)

    if request.GET.get('topic'):
        projects = projects.filter(topic__topic = request.GET['topic'])

    if request.GET.get('status') and int(request.GET.get('status')) > 0:
        projects = projects.filter(status = request.GET['status'])

    if request.GET.get('country'):
        projects = projects.filter(country = request.GET['country'])

    if request.GET.get('doingAtHome'):
        projects = projects.filter(doingAtHome = request.GET['doingAtHome'])

    if request.GET.get('approvedCheck'):
        if request.GET['approvedCheck'] == 'On':
            projects = projects.filter(id__in=approvedProjects)
        if request.GET['approvedCheck'] == 'Off':
            projects = projects.exclude(id__in=approvedProjects)
        if request.GET['approvedCheck'] == 'All':
            projects = projects
    else:
        projects = projects.filter(id__in=approvedProjects)

    return projects

def setFilters(request, filters):
    if request.GET.get('topic'):
        filters['topic'] = request.GET['topic']
    if request.GET.get('status'):
        filters['status'] =  int(request.GET['status'])
    if request.GET.get('doingAtHome'):
        filters['doingAtHome'] = int(request.GET['doingAtHome'])
    if request.GET.get('country'):
        filters['country'] = request.GET['country']
    if request.GET.get('approvedCheck'):
        filters['approvedCheck'] = request.GET['approvedCheck']
    return filters

def clearFilters(request):
    return redirect ('projects')

@staff_member_required()
def setApproved(request):
    response = {}
    id = request.POST.get("project_id")
    approved = request.POST.get("approved")
    setProjectApproved(id, approved)
    return JsonResponse(response, safe=False)

def setProjectApproved(id, approved):
    approved= False if approved in ['False','false','0'] else True
    aProject = get_object_or_404(Project, id=id)
    if approved == True:
        #Insert
        ApprovedProjects.objects.get_or_create(project=aProject)
        #Delete UnApprovedProjects
        try:
            obj = UnApprovedProjects.objects.get(project_id=id)
            obj.delete()
        except UnApprovedProjects.DoesNotExist:
            print("Does not exist this unapproved project")
    else:
        #Insert UnApprovedProjects
        UnApprovedProjects.objects.get_or_create(project=aProject)
        #Delete
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

def setProjectFeatured(id, featured):
    project = get_object_or_404(Project, id=id)
    project.featured = featured
    project.featured = False if featured in ['False','false','0'] else True
    project.save()

def setFollowedProject(request):
    response = {}
    projectId = request.POST.get("project_id")
    userId = request.POST.get("user_id")
    follow = request.POST.get("follow")
    followProject(projectId, userId, follow)
    return JsonResponse(response, safe=False)

def followProject(projectId, userId, follow):
    follow= False if follow in ['False','false','0'] else True
    fProject = get_object_or_404(Project, id=projectId)
    fUser = get_object_or_404(User, id=userId)
    if follow == True:
        #Insert
        followedProject = FollowedProjects.objects.get_or_create(project=fProject, user=fUser)
    else:
        #Delete
        try:
            obj = FollowedProjects.objects.get(project_id=projectId,user_id=userId)
            obj.delete()
        except FollowedProjects.DoesNotExist:
            print("Does not exist this followed project")


def allowUser(request):
    response = {}
    projectId = request.POST.get("project_id")
    users = request.POST.get("users")
    project = get_object_or_404(Project, id=projectId)

    if request.user != project.creator and not request.user.is_staff:
        #TODO return JsonResponse with error code
        return redirect('../projects', {})

    #Delete all
    objs = ProjectPermission.objects.all().filter(project_id=projectId)
    if(objs):
        for obj in objs:
            obj.delete()

    #Insert all
    users = users.split(',')
    for user in users:
        fUser = User.objects.filter(email=user)[:1].get()
        projectPermission = ProjectPermission(project=project, user=fUser)
        projectPermission.save()

    return JsonResponse(response, safe=False)

def project_review(request, pk):
    return render(request, 'project_review.html', {'projectID': pk})

### Download all projects in a CSV file
def downloadProjects(request):
    projects = Project.objects.get_queryset()

    response = StreamingHttpResponse(
        streaming_content=(iter_items(projects, Buffer())),
        content_type='text/csv',
    )
    response['Content-Disposition'] = 'attachment; filename="projects.csv"'
    return response

def get_headers():
    return ['id', 'name', 'aim', 'description', 'keywords','status', 'start_date', 'end_date', 'topic', 'url', 'country',
     'host', 'howToParticipate', 'doingAtHome', 'equipment', 'fundingBody', 'fundingProgram', 'originDatabase', 'originURL', 'originUID']

def get_data(item):
    keywordsList = list(item.keywords.all().values_list('keyword', flat=True))
    topicList = list(item.topic.all().values_list('topic', flat=True))
    participationtaskList = list(item.participationtask.all().values_list('participationtask', flat=True))
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
        'participationtask' : participationtaskList,
        'geographicextend' : geographicextendList,
        'url': item.url,
        'projectlocality': item.projectlocality,
        'country': item.country,
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

def getOrganisations(request):
    mainOrganisation = request.GET.getlist("mainOrganisation[]")
    if(mainOrganisation):
        mainOrganisation = mainOrganisation[0]
    else:
        mainOrganisation = request.GET.get("mainOrganisation")
    organisationsSelected = request.GET.getlist("organisationsSelected[]")
    organisationsSelected = list(organisationsSelected)
    organisationsSelected = ", ".join(organisationsSelected)
    options = '<select id="id_organisation" class="select form-control">'
    response = {}
    organisations = Organisation.objects.get_queryset()
    organisations = organisations.values_list("id","name")
    organisations = tuple(organisations)
    if organisations:        
        for organisation in organisations:
            if(not mainOrganisation or int(organisation[0]) != int(mainOrganisation)):
                if(str(organisation[0]) in organisationsSelected):
                    options += '<option value = "%s" selected>%s</option>' % (
                        organisation[0],
                        organisation[1]
                    )
                else:
                    options += '<option value = "%s">%s</option>' % (
                        organisation[0],
                        organisation[1]
                    )
        options += '</select>'
        response['organisations'] = options
    else:
        response['organisations'] = '<select id="id_organisation" class="select form-control" disabled></select>'

    return JsonResponse(response)


def getKeywordsSelector(request):
    project_id = request.GET.get("project_id")
    keywordsSelected = []
    if project_id != '0':
        project = get_object_or_404(Project, id=project_id)
        keywordsSelected = list(project.keywords.all().values_list('keyword', flat=True))
    
    options = '<select id="id_keywords" class="select form-control">'
    response = {}
    keywords = Keyword.objects.get_queryset()
    keywords = keywords.values_list("id","keyword")
    keywords = tuple(keywords)
    if keywords:
        for keyword in keywords:
            found = False
            if(keywordsSelected):                
                for key in keywordsSelected:
                    if(str(keyword[1]) == key):
                        found=True
                        options += '<option value = "%s" selected>%s</option>' % (
                            keyword[0],
                            keyword[1]
                        )
                        break
            if(not found or not keywordsSelected):
                options += '<option value = "%s">%s</option>' % (
                    keyword[0],
                    keyword[1]
                )
        options += '</select>'
        response['keywords'] = options
    else:
        response['keywords'] = '<select id="id_keywords" class="select form-control" disabled></select>'

    return JsonResponse(response)
