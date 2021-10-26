from django.views import generic
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from itertools import chain
from projects.models import Project, ApprovedProjects
from projects.views import getProjectsAutocomplete
from resources.views import getResourcesAutocomplete
from organisations.views import getOrganisationAutocomplete
from platforms.views import getPlatformsAutocomplete
from profiles.views import getProfilesAutocomplete
from resources.models import Resource, ResourceGroup, ResourcesGrouped
from resources.models import ApprovedResources, SavedResources, Theme, Category
from organisations.models import Organisation
from platforms.models import Platform
from django.conf import settings
from blog.models import Post
import random
import json
from machina.apps.forum.models import Forum
from machina.apps.forum_conversation.models import Topic, Post
from machina.apps.forum_tracking.models import TopicReadTrack
from machina.apps.forum_tracking.handler import TrackingHandler


def home(request):
    # Projects
    user = request.user
    projects = Project.objects.get_queryset().filter(~Q(hidden=True)).order_by('-dateCreated')
    approvedProjects = ApprovedProjects.objects.all().values_list('project_id', flat=True)
    projects = projects.filter(id__in=approvedProjects)

    filters = {'keywords': ''}

    # if request.GET.get('keywords'):
    #    projects = projects.filter( Q(name__icontains = request.GET['keywords']) |
    #                                Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
    #    filters['keywords'] = request.GET['keywords']
    counterprojects = len(projects)
    paginatorprojects = Paginator(projects, 4)
    page = request.GET.get('page')
    projects = paginatorprojects.get_page(page)

    # Resources
    resources = Resource.objects.get_queryset().filter(
            ~Q(isTrainingResource=True)).filter(~Q(hidden=True)).order_by('-dateUploaded')
    approvedResources = ApprovedResources.objects.all().values_list('resource_id', flat=True)
    resources = resources.filter(id__in=approvedResources)
    # savedResources = None
    # savedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id',flat=True)
    # languagesWithContent = Resource.objects.all().values_list('inLanguage', flat=True).distinct()
    # themes = Theme.objects.all()
    # categories = Category.objects.all()
    # if request.GET.get('keywords'):
    #    resources = resources.filter( Q(name__icontains = request.GET['keywords'])  |
    #                                Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
    #    filters['keywords'] = request.GET['keywords']
    counterresources = len(resources)
    paginatorresources = Paginator(resources, 4)
    page = request.GET.get('page')
    resources = paginatorresources.get_page(page)

    # Training Resources
    trainingResources = Resource.objects.get_queryset().filter(isTrainingResource=True).order_by('-dateUploaded')
    tapprovedResources = ApprovedResources.objects.all().values_list('resource_id', flat=True)
    trainingResources = trainingResources.filter(id__in=tapprovedResources)
    # tsavedResources = None
    # tsavedResources = SavedResources.objects.all().filter(user_id=user.id).values_list('resource_id',flat=True)
    # if request.GET.get('keywords'):
    #     tresources = tresources.filter( Q(name__icontains = request.GET['keywords'])  |
    #                                Q(keywords__keyword__icontains = request.GET['keywords']) ).distinct()
    #    filters['keywords'] = request.GET['keywords']

    trainingResources = trainingResources.filter(~Q(hidden=True))
    # tresourcesTop = tresources.filter(featured=True)
    # tresourcesTopIds = list(tresourcesTop.values_list('id',flat=True))
    # tresources = tresources.exclude(id__in=tresourcesTopIds)
    # tresources = list(tresourcesTop) + list(tresources)
    countertresources = len(trainingResources)
    paginatorTrainingResources = Paginator(trainingResources, 4)
    page = request.GET.get('page')
    trainingResources = paginatorTrainingResources.get_page(page)

    # Organisations
    # TODO: Put -dateCreated
    organisations = Organisation.objects.all().order_by('id')
    if request.GET.get('keywords'):
        organisations = organisations.filter(Q(name__icontains=request.GET['keywords'])).distinct()
    counterorganisations = len(organisations)
    paginatororganisation = Paginator(organisations, 4)
    page = request.GET.get('page')
    organisations = paginatororganisation.get_page(page)

    # Platforms
    platforms = Platform.objects.all().order_by('-dateCreated')
    counterPlatforms = len(platforms)
    paginatorPlatform = Paginator(platforms, 4)
    page = request.GET.get('page')
    platforms = paginatorPlatform.get_page(page)

    total = countertresources + counterprojects + countertresources + counterorganisations

    return render(request, 'home.html', {
        'user': user,
        'projects': projects,
        'counterprojects': counterprojects,
        'resources': resources,
        'counterresources': counterresources,
        'filters': filters,
        'trainingResources': trainingResources,
        'countertresources': countertresources,
        'organisations': organisations,
        'counterorganisations': counterorganisations,
        'platforms': platforms,
        'counterPlatforms': counterPlatforms,
        'total': total,
        'isSearchPage': True})


def all(request):
    return home(request)


class AboutPage(generic.TemplateView):
    template_name = "about.html"


def curated(request):
    groups = ResourceGroup.objects.get_queryset().order_by('id')
    resourcesgrouped = ResourcesGrouped.objects.get_queryset().order_by('group')
    return render(request, 'curated.html', {
        'groups': groups,
        'resourcesgrouped': resourcesgrouped,
        'isSearchPage': False})


def imprint(request):
    return render(request, 'imprint.html')


def contact(request):
    return render(request, 'contact.html')


def terms(request):
    return render(request, 'terms.html')


def privacy(request):
    return render(request, 'privacy.html')


def faq(request):
    return render(request, 'faq.html')


def development(request):
    return render(request, 'development.html')


def subscribe(request):
    return render(request, 'subscribe.html')


def moderation(request):
    return render(request, 'moderation.html')


def policy_brief(request):
    return render(request, 'policy_brief.html')


def criteria(request):
    return render(request, 'criteria.html')


def moderation_quality_criteria(request):
    return render(request, 'moderation_quality_criteria.html')


def translations(request):
    return render(request, 'translations.html')


def call(request):
    return render(request, 'call.html')


def policy_maker_event_2021(request):
    return render(request, 'policy_maker_event_2021.html')


def final_launch(request):
    return render(request, 'final_launch.html')


def home_autocomplete(request):
    if request.GET.get('q'):
        text = request.GET['q']
        projects = getProjectsAutocomplete(text)
        resources = getResourcesAutocomplete(text, False)
        training = getResourcesAutocomplete(text, True)
        organisations = getOrganisationAutocomplete(text)
        platforms = getPlatformsAutocomplete(text)
        profiles = getProfilesAutocomplete(text)
        report = chain(resources, projects, training, organisations, platforms, profiles)
        response = list(report)
        return JsonResponse(response, safe=False)
    else:
        return HttpResponse("No cookies")


def getTopicsResponded(request):
    response = {}
    topics = {}
    if not request.user.is_anonymous and not request.user.is_staff:
        own_topics = Topic.objects.get_queryset().filter(status=0, poster_id=request.user, posts_count__gt=1)
        suscribed_topics = request.user.topic_subscriptions.all()
        result = own_topics | suscribed_topics
        result = result.distinct()
        topics = TrackingHandler.get_unread_topics(request, result, request.user)

    topicshtml = "</br>"

    for topic in topics:
        slug = '' + topic.slug + '-' + str(topic.id)
        forum = get_object_or_404(Forum, id=topic.forum_id)
        forum_slug = forum.slug + '-' + str(forum.id)
        topicshtml += '<p class="alert alert-info" role="alert">There is a response in a topic that you follow' \
        ' <a href="' + settings.HOST + '/forum/forum/' + forum_slug + '/topic/'+ slug + '">%s</a></p>' % (
                        topic.subject
                    )

    response['topics'] = topicshtml
    return JsonResponse(response)


def getForumResponsesNumber(request):
    response = {}
    forumresponses = 0
    if not request.user.is_anonymous and not request.user.is_staff:
        own_topics = Topic.objects.get_queryset().filter(status=0, poster_id=request.user, posts_count__gt=1)
        suscribed_topics = request.user.topic_subscriptions.all()
        result = own_topics | suscribed_topics
        result = result.distinct()
        result = TrackingHandler.get_unread_topics(request, result, request.user)
        forumresponses = len(result)

    response['forumresponses'] = forumresponses
    return JsonResponse(response)
