from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from .models import Digest
from blog.models import Post
from events.models import Event
from projects.models import Project
from resources.models import Resource
from organisations.models import Organisation
from dateutil.relativedelta import relativedelta


# Create your views here.


def showDigests(request):

    return render(request, 'show_digests.html')


def showDigest(request, pk, mode='page'):
    digest = get_object_or_404(Digest, id=pk)
    info = {"digest": digest, "domain": settings.HOST}

    if(digest.includePosts):
        posts = Post.objects.filter(
            status=1,
            created_on__range=(digest.dateOrg, digest.dateEnd))
        info["posts"] = posts

    if(digest.includeEvents):
        events = Event.objects.filter(
            approved=True,
            end_date__range=(digest.dateEnd, digest.dateEnd+relativedelta(months=+2)))
        info["events"] = events

    if(digest.includeOrganisations):
        organisations = Organisation.objects.filter(
            dateCreated__range=(digest.dateOrg, digest.dateEnd))
        info["organisations"] = organisations

    if(digest.includeProjects):
        projects = Project.objects.filter(
            approved=True,
            dateCreated__range=(digest.dateOrg, digest.dateEnd))
        print(projects.query)
        info["projects"] = projects

    if(digest.includeResources):
        resources = Resource.objects.filter(
            isTrainingResource=False,
            approved=True,
            dateUploaded__range=(digest.dateOrg, digest.dateEnd))
        info["resources"] = resources

    if(digest.includeTrainings):
        training = Resource.objects.filter(
            isTrainingResource=True,
            approved=True,
            dateUploaded__range=(digest.dateOrg, digest.dateEnd))
        info["training"] = training

    print(info)

    if mode == 'string':
        return render_to_string('show_digest.html', info)
    else:
        return render(request, 'show_digest.html', info)
