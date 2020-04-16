from django.shortcuts import render, redirect
from .models import Event
from .forms import EventForm

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

def events(request):
    user = request.user
    events = Event.objects.get_queryset()

    return render(request, 'events.html', {'events': events, 'user':user})