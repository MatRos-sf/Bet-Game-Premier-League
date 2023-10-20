from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import League, Team, Season, Team_Stats


class LeagueListView(LoginRequiredMixin, ListView):
    model = League
    template_name = ''
    context_object_name = 'leagues/'
    #ordering = ['-season']


class LeagueDetailView(LoginRequiredMixin, ListView):
    model = League
    template_name = "league/"


class LeagueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = League
    template_name = 'league/'
    fields = ['name', 'country', 'emblem']

    def test_func(self):
        return self.request.user.is_superuser()


