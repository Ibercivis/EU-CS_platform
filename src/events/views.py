from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import formats
from .models import Event, ApprovedEvents, UnApprovedEvents
from .forms import EventForm


def events(request):
    user = request.user
    now = datetime.today()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    events = Event.objects.get_queryset().filter(start_date__gt=now).order_by('-featured', 'start_date')
    ongoingEvents = Event.objects.get_queryset().filter(
            start_date__lte=now,
            end_date__gte=now).order_by('-featured', 'start_date')
    pastEvents = Event.objects.get_queryset().order_by('-featured', '-start_date')
    print(pastEvents)
    approvedEvents = ApprovedEvents.objects.all().values_list('event_id', flat=True)
    unApprovedEvents = UnApprovedEvents.objects.all().values_list('event_id', flat=True)

    if not user.is_staff:
        events = events.exclude(id__in=unApprovedEvents)

    return render(request, 'events.html', {
        'events': events,
        'pastEvents': pastEvents,
        'ongoingEvents': ongoingEvents,
        'approvedEvents': approvedEvents,
        'unApprovedEvents': unApprovedEvents,
        'user': user})


@login_required(login_url='/login')
def new_event(request):
    user = request.user
    form = EventForm()
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('/events')
        else:
            print(form.errors)
    return render(request, 'new_event.html', {'form': form, 'user': user})


def editEvent(request, pk):
    user = request.user
    event = get_object_or_404(Event, id=pk)

    if user != event.creator and not user.is_staff:
        return redirect('../events', {})

    start_datetime = None
    end_datetime = None
    if event.start_date:
        start_datetime = formats.date_format(event.start_date, 'Y-m-d')
    if event.end_date:
        end_datetime = formats.date_format(event.end_date, 'Y-m-d')
    form = EventForm(initial={
        'title': event.title,
        'description': event.description,
        'place': event.place,
        'start_date': start_datetime,
        'end_date': end_datetime,
        'hour': event.hour,
        'url': event.url})
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('/events')
        else:
            print(form.errors)
    return render(request, 'editEvent.html', {'form': form, 'user': user, 'event': event})


def deleteEvent(request, pk):
    obj = get_object_or_404(Event, id=pk)
    if request.user == obj.creator or request.user.is_staff:
        obj.delete()
    return redirect('events')


@staff_member_required()
def setFeaturedEvent(request):
    response = {}
    id = request.POST.get("event_id")
    featured = request.POST.get("featured")
    event = get_object_or_404(Event, id=id)
    event.featured = False if featured == 'false' else True
    event.save()
    return JsonResponse(response, safe=False)


@staff_member_required()
def setApprovedEvent(request):
    response = {}
    id = request.POST.get("event_id")
    approved = request.POST.get("approved")
    setApprovedOrUnapprovedEvent(id, approved)
    return JsonResponse(response, safe=False)


def setApprovedOrUnapprovedEvent(id, approved):
    approved = False if approved in ['False', 'false', '0'] else True
    aEvent = get_object_or_404(Event, id=id)
    if approved is True:
        # Insert
        ApprovedEvents.objects.get_or_create(event=aEvent)
        # Delete UnApprovedEvents
        try:
            obj = UnApprovedEvents.objects.get(event_id=id)
            obj.delete()
        except UnApprovedEvents.DoesNotExist:
            print("Does not exist this unapproved event")
        # TODO: Why we need an external OneToOne? Delete?
        aEvent.approved = 'True'
        aEvent.save()
    else:
        # Insert UnApprovedEvents
        UnApprovedEvents.objects.get_or_create(event=aEvent)
        # Delete
        try:
            obj = ApprovedEvents.objects.get(event_id=id)
            obj.delete()
        except ApprovedEvents.DoesNotExist:
            print("Does not exist this approved event")
        aEvent.approved = 'False'
        aEvent.save()
