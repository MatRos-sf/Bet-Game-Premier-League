from django.contrib import admin
from .models import League, Team, Season, TeamStats

admin.site.register(League)
admin.site.register(Team)
admin.site.register(Season)
admin.site.register(TeamStats)
