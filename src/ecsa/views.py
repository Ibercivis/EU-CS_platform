from django.shortcuts import render
from datetime import date
from .models import InvoiceCounter


def getEcsaInvoiceCounter():
    currentYear = date.today().year
    try:
        invoiceCounter = InvoiceCounter.objects.get(id=1)
    except InvoiceCounter.DoesNotExist:
        invoiceCounter = InvoiceCounter(1,currentYear)
        return invoiceCounter.counter
    
    if (invoiceCounter.year < currentYear):
        invoiceCounter.year = currentYear
        invoiceCounter.counter = 1
    else:
        invoiceCounter.counter+=1
    invoiceCounter.save()
    return invoiceCounter.counter