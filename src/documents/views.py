from django.shortcuts import render
from .models import Document
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .forms import DocumentForm
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib import messages


def documents(request):
    documents = Document.objects.all()
    return render(request, 'documents.html', {'documents':documents})

def new_document(request):
    form = DocumentForm()
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request)
            messages.success(request, "Document uploaded with success!")
            return redirect('/documents')

    return render(request, 'new_document.html', {'form': form})
