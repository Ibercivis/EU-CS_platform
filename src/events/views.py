from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.conf import settings
from django.utils import formats
from .models import Event, HelpText, ApprovedEvents, UnApprovedEvents
from .forms import EventForm
from django.db.models import Q


def events(request):
    user = request.user
    now = datetime.today()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    query = request.GET.get("q") or ""
    events = Event.objects.get_queryset().filter(start_date__gt=now).order_by('-featured', 'start_date')
    ongoingEvents = Event.objects.get_queryset().filter(
        start_date__lte=now,
        end_date__gte=now).order_by('-featured', 'start_date')
    pastEvents = Event.objects.get_queryset().order_by('-featured', '-start_date')

    filters = {'q':'', 'country': '', 'language': '', 'event_type': '', 'project': '', 'organisation': ''}
    cwc = set(Event.objects.exclude(country=None).values_list('country', flat=True))
    languages = list(set(Event.objects.values_list('language', flat=True)))
    projects = list(set(Event.objects.values_list('project__name', flat=True)))
    organisations = organisations = list(set(Event.objects.values_list('organisations__name', flat=True).union(Event.objects.values_list('mainOrganisation__name', flat=True))))
    # remove None if it exists in the lists
    projects = [project for project in projects if project is not None]
    organisations = [org for org in organisations if org is not None]
    print(languages)

    events = applyFilters(request, events).filter(start_date__gt=now)
    ongoingEvents = applyFilters(request, ongoingEvents).filter(start_date__lte=now, end_date__gte=now)
    pastEvents = applyFilters(request, pastEvents).filter(end_date__lt=now)
    filters = setFilters(request, filters)

    total_events = len(ongoingEvents) + len(events) + len(pastEvents)
    num_upcomingEvents = len(events)
    num_ongoingEvents = len(ongoingEvents)
    num_pastEvents = len(pastEvents)
    '''
    ongoingEvents = Event.objects.get_queryset().filter(
            start_date__lte=now,
            end_date__gte=now).order_by('-featured', 'start_date')
    pastEvents = Event.objects.get_queryset().order_by('-featured', '-start_date')
    '''
    paginator = Paginator(pastEvents, 12) # 3 son los elementos que se muestran por página.
    page = request.GET.get('page')
    try:
        pastEvents = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, entrega la primera página.
        pastEvents = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango (por ejemplo, 9999), entrega la última página de resultados.
        pastEvents = paginator.page(paginator.num_pages)
    print(pastEvents)
    approvedEvents = ApprovedEvents.objects.all().values_list('event_id', flat=True)
    unApprovedEvents = UnApprovedEvents.objects.all().values_list('event_id', flat=True)

    

    if not user.is_staff:
        events = events.exclude(id__in=unApprovedEvents)

    return TemplateResponse(request, 'events.html', {
        'q': query,
        'total_events': total_events,
        'num_upcomingEvents': num_upcomingEvents,
        'num_ongoingEvents': num_ongoingEvents,
        'num_pastEvents': num_pastEvents,
        'cwc': cwc,
        'languages': languages,
        'projects': projects,
        'organisations': organisations,
        'filters': filters,
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
    text = get_object_or_404(HelpText, slug='new-event')
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('/events')
        else:
            print(form.errors)
    return TemplateResponse(request, 'new_event.html', {
        'form': form, 
        'user': user,
        'text': text,
        'user_agent': settings.USER_AGENT})


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
        'country': event.country,
        'language': event.language,
        'event_type': event.event_type,
        'project': event.project,
        'organisations': event.organisations.all(),
        'mainOrganisation': event.mainOrganisation,
        'timezone': event.timezone,
        'latitude': event.latitude,
        'longitude': event.longitude,
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
    return render(request, 'editEvent.html', {'form': form, 'user': user, 'event': event, 'user_agent': settings.USER_AGENT})


def deleteEvent(request, pk):
    obj = get_object_or_404(Event, id=pk)
    if request.user == obj.creator or request.user.is_staff:
        obj.delete()
    return redirect('events')

def applyFilters(request, queryset):
    if request.GET.get("q"):
        queryset = queryset.filter(
            Q(title__icontains=request.GET.get("q")) |
            Q(description__icontains=request.GET.get("q")) |
            Q(place__icontains=request.GET.get("q"))
        ).distinct()       
    if request.GET.getlist('country[]'):
        print(request.GET.getlist('country[]'))
        if request.GET.get('event_type') == '':
            queryset = queryset.filter(
                Q(event_type='online') |
                Q(event_type='face-to-face', country__in=request.GET.getlist('country[]'))
            ).distinct()
        elif request.GET['event_type'] == 'online':
            queryset = queryset.filter(Q(event_type='online', country__in=request.GET.getlist('country[]'))).distinct()
        elif request.GET['event_type'] == 'face-to-face':
            queryset = queryset.filter(Q(event_type='face-to-face', country__in=request.GET.getlist('country[]'))).distinct()

    if request.GET.getlist('language[]'):
        print(request.GET.getlist('language[]'))
        queryset = queryset.filter(language__in=request.GET.getlist('language[]')).distinct()

    if request.GET.get('event_type'):
        if request.GET['event_type'] == 'online':
            queryset = queryset.filter(event_type='online').distinct()
        elif request.GET['event_type'] == 'face-to-face':
            queryset = queryset.filter(event_type='face-to-face').distinct()

    if request.GET.getlist('project[]'):
        queryset = queryset.filter(project__name__in=request.GET.getlist('project[]')).distinct()

    if request.GET.getlist('organisation[]'):
        queryset = queryset.filter(
            Q(organisations__name__in=request.GET.getlist('organisation[]')) |
            Q(mainOrganisation__name__in=request.GET.getlist('organisation[]'))).distinct()
    
    return queryset

def setFilters(request, filters):
    if request.GET.get("q"):
        filters['q'] = request.GET.get("q")
    if request.GET.getlist('country[]'):
        filters['country'] = request.GET.getlist('country[]')
    if request.GET.getlist('language[]'):
        filters['language'] = request.GET.getlist('language[]')
    if request.GET.get('event_type'):
        filters['event_type'] = request.GET['event_type']
    if request.GET.getlist('project[]'):
        filters['project'] = request.GET.getlist('project[]')
    if request.GET.getlist('organisation[]'):
        filters['organisation'] = request.GET.getlist('organisation[]')  
    return filters


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
