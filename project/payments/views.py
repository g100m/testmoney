# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic.edit import FormView
from .forms import AmountFromUser
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect


class IndexView(FormView):
    form_class = AmountFromUser
    template_name = 'index.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        super(IndexView, self).form_valid(form)
        form.process()
        return HttpResponseRedirect(reverse_lazy('index'))
