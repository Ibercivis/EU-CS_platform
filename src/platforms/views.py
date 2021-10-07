from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import PlatformForm

# Create your views here.


@login_required(login_url='/login')
def newPlatform(request):
    user = request.user
    platformForm = PlatformForm()

    return render(request, 'platform_form.html', {'form': platformForm, 'user': user})
