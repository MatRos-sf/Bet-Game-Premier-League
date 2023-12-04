from django.contrib import admin
from .models import Bet


class BetAdmin(admin.ModelAdmin):
    raw_id_fields = ["match", "user"]


admin.site.register(Bet, BetAdmin)
