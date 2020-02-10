# -*- coding: utf-8 -*-
from __future__ import division

from decimal import Decimal

from django import forms
from django.core.validators import MinValueValidator, RegexValidator
from django.db import transaction

from .models import User


class AmountFromUser(forms.Form):
    from_user = forms.ChoiceField(
        label=u'Списать с',
        required=True,
    )

    amount = forms.DecimalField(
        label=u'Сумма списания', max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))],
    )

    to_users = forms.CharField(
        label=u'ИНН получателей',
        required=True,
        validators=[
            RegexValidator(
                regex='[\d\s,]',
                message='Поле может содержать только цифры и разделители',
            ),
        ],
    )

    def clean(self):

        cleaned_data = super(AmountFromUser, self).clean()

        from_user = cleaned_data.get("from_user")
        amount = cleaned_data.get("amount")
        to_users = cleaned_data.get("to_users", '').strip()

        try:
            from_user = User.objects.get(pk=from_user)
            if from_user.amount <= 0 or from_user.amount < amount:
                raise forms.ValidationError(u"""Баланс пользователя не позволяет совершить операцию""")

        except User.DoesNotExist:
            raise forms.ValidationError(u"""Пользователь не найден""")

        if not to_users:
            raise forms.ValidationError(u"""Необходимо указать получателей""")

        if not User.objects.filter(inn__in=[int(inn) for inn in to_users.split(' ,')]):
            raise forms.ValidationError(u"""Пользователи с указанным ИНН не найдено""")

    def __init__(self, *args, **kwargs):

        super(AmountFromUser, self).__init__(*args, **kwargs)
        self.fields['from_user'].choices = ((us['id'], us['name']) for us in User.objects.values('id', 'name').all())

    def process(self):

        to_users = self.cleaned_data.get('to_users')
        to_users = User.objects.filter(inn__in=[int(inn) for inn in to_users.split(' ,')])

        from_user = User.objects.get(pk=self.cleaned_data.get('from_user'))
        amount = self.cleaned_data.get('amount')
        amount_to_user = amount / len(to_users)

        with transaction.atomic():
            from_user.update_amount(-1 * amount)
            for to_user in to_users:
                to_user.update_amount(amount_to_user)
