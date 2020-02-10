# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.db import models
from django.db.models import F


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    inn = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    USERNAME_FIELD = 'name'

    def update_amount(self, amount):
        self.amount = F('amount') + amount
        self.save(update_fields=['amount'])

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name
