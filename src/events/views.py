from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import formats
from .models import Event
from .forms import EventForm


def events(request):
    user = request.user
    events = Event.objects.get_queryset().order_by('-featured','start_date')

    return render(request, 'events.html', {'events': events, 'user':user})

@staff_member_required()
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
    return render(request, 'new_event.html', {'form': form, 'user':user})

@staff_member_required()
def editEvent(request, pk):
    user = request.user
    event = get_object_or_404(Event, id=pk)
    start_datetime = None
    end_datetime = None
    if event.start_date:
        start_datetime = formats.date_format(event.start_date, 'Y-m-d')
    if event.end_date:
        end_datetime = formats.date_format(event.end_date, 'Y-m-d')
    form = EventForm(initial={'title': event.title, 'description': event.description, 'place': event.place,
                    'start_date': start_datetime, 'end_date': end_datetime, 'hour': event.hour, 'url': event.url})
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('/events')
        else:
            print(form.errors)
    return render(request, 'editEvent.html', {'form': form, 'user':user, 'event': event})

@staff_member_required()
def deleteEvent(request, pk):
    obj = get_object_or_404(Event, id=pk)
    if request.user.is_staff:
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