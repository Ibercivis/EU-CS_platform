from django.contrib import admin
from .models import Delegate, Ecsa_fee, InvoiceCounter
from django.utils.html import mark_safe
from organisations.models import Organisation
from django.db.models import Q

class Ecsa_feeAdmin(admin.ModelAdmin):
    model = Ecsa_fee
    list_display = (
        "membership",
        "amount",
    )


class InvoiceCounterAdmin(admin.ModelAdmin):
    model = InvoiceCounter
    list_display = (
        "counter",
        "year",
    )

class DelegateA(admin.ModelAdmin):    
    list_display = ('name', 'email', 'user', 'main_delegate_of', 'delegate_of')
    def main_delegate_of(self, obj):
        to_return = '\n'.join('<p>{}</p>'.format(aux.name) for aux in Organisation.objects.all().filter(mainDelegate=obj))
        return mark_safe(to_return)
    def delegate_of(self, obj):
        to_return = '\n'.join('<p>{}</p>'.format(aux.name) for aux in Organisation.objects.all().filter(Q(delegate1=obj) | Q(delegate2=obj)))
        return mark_safe(to_return) 




admin.site.register(Ecsa_fee,Ecsa_feeAdmin)
admin.site.register(InvoiceCounter,InvoiceCounterAdmin)
admin.site.register(Delegate, DelegateA)