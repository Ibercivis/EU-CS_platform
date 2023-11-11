from django.views import generic
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from itertools import chain
from projects.models import Project, ApprovedProjects, Likes, Follows
from projects.views import getProjectsAutocomplete
from resources.views import getResourcesAutocomplete
from organisations.views import getOrganisationAutocomplete
from platforms.views import getPlatformsAutocomplete
from profiles.views import getProfilesAutocomplete
from resources.models import Resource, ResourceGroup, ResourcesGrouped
from resources.models import ApprovedResources, SavedResources, Theme, Category
from organisations.models import Organisation
from platforms.models import Platform
from profiles.models import Profile
from django.conf import settings
from blog.models import Post
from eucitizensciencetheme.models import TopBar
import random
import json
from django.template.loader import render_to_string
from machina.apps.forum.models import Forum
from machina.apps.forum_conversation.models import Topic, Post
from machina.apps.forum_tracking.models import TopicReadTrack
from machina.apps.forum_tracking.handler import TrackingHandler


class AboutPage(generic.TemplateView):
    template_name = "about.html"


def curated(request):
    groups = ResourceGroup.objects.get_queryset().order_by('id')
    resourcesgrouped = ResourcesGrouped.objects.get_queryset().order_by('group')

    filters = {
        'keywords': '',
    }

    return TemplateResponse(request, 'curated.html', {
        'groups': groups,
        'resourcesgrouped': resourcesgrouped,
        'filters': filters,
        'isSearchPage': False})

def contact(request):
    return TemplateResponse(request, 'contact.html')

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

