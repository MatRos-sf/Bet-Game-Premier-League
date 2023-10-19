from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import League, LeagueTable, Team


class LeagueListView(LoginRequiredMixin, ListView):
    model = League
    template_name = ''
    context_object_name = 'leagues'
    ordering = ['-season']

class LeagueDetailView(LoginRequiredMixin, ListView):
    model = League
    template_name = "league/"