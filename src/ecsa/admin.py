from django.contrib import admin
from .models import Delegate, Ecsa_fee, InvoiceCounter

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

admin.site.register(Ecsa_fee,Ecsa_feeAdmin)
admin.site.register(InvoiceCounter,InvoiceCounterAdmin)
admin.site.register(Delegate)