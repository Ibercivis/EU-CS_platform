from django.contrib import admin
from .models import Ecsa_fee

class Ecsa_feeAdmin(admin.ModelAdmin):
    model = Ecsa_fee
    list_display = (
        "membership",
        "amount",
    )

admin.site.register(Ecsa_fee,Ecsa_feeAdmin)
