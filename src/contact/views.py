from django.shortcuts import render
from django.views import generic
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from resources.models import Resource
from projects.models import Project
from events.models import Event
from .forms import ContactForm, SubmitterContactForm

def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = 'contact form'
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            message += '<br/><br/>' + name + ' ' + surname + ', ' + from_email
            try:
                send_mail(subject, message, from_email, settings.EMAIL_CONTACT_RECIPIENT_LIST, html_message=message)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('success')
    return render(request, "contact.html", {'form': form})

class SuccessPage(generic.TemplateView):
    template_name = "success.html"


def submitterContactView(request, group, pk):
    referenceURL = settings.HOST + '/' + group + '/' + str(pk)
    if request.method == 'GET':
        form = SubmitterContactForm()
    else:
        form = SubmitterContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            if (group =="project"):
                project = get_object_or_404(Project, id=pk)
                to_email = project.creator.email
            elif(group =="resource"):
                resource = get_object_or_404(Resource, id=pk)
                to_email = resource.creator.email
            else:
                event = get_object_or_404(Event, id=pk)
                to_email = event.creator.email
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [to_email])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('success')
    return render(request, "submitter_contact.html", {'form': form, 'referenceURL': referenceURL})
