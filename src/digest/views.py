from django.shortcuts import render, get_object_or_404
from .models import Digest
from projects.models import Project
from resources.models import Resource


# Create your views here.


def showDigests(request):

    return render(request, 'show_digests.html')


def showDigest(request, pk):
    digest = get_object_or_404(Digest, id=pk)
    info = {}
    if(digest.hasProjects):
        projects = Project.objects.filter(
            dateCreated__range=(digest.dateOrg, digest.dateEnd))
        print(projects.query)
        info["projects"] = projects

    if(digest.hasResources):
        resources = Resource.objects.filter(
            dateUploaded__range=(digest.dateOrg, digest.dateEnd))
        info["resources"] = resources
    print(info)

    return render(request, 'show_digest.html', info)
