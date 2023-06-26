import datetime

from django import forms
from django.conf import settings

from .models import Transaction

from accounts.models import UserBankAccount


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transfer_to',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):

    def clean_amount(self):
        min_deposit_amount = settings.MINIMUM_DEPOSIT_AMOUNT
        amount = self.cleaned_data.get('amount')

        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least Rs.{min_deposit_amount} '
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_amount = settings.MINIMUM_WITHDRAWAL_AMOUNT
        max_amount = (
            account.account_type.maximum_withdrawal_or_transfer_amount
        )
        balance = account.balance

        amount = self.cleaned_data.get('amount')

        if amount < min_amount:
            raise forms.ValidationError(
                f'You can withdraw at least Rs.{min_amount} '
            )

        if amount > max_amount:
            raise forms.ValidationError(
                f'You can withdraw at most Rs.{max_amount} '
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have Rs.{balance}  in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount


class TransferForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_amount = settings.MINIMUM_TRANSFER_AMOUNT
        max_amount = (
            account.account_type.maximum_withdrawal_or_transfer_amount
        )
        balance = account.balance

        amount = self.cleaned_data.get('amount')

        if amount < min_amount:
            raise forms.ValidationError(
                f'You can withdraw at least Rs.{min_amount} '
            )

        if amount > max_amount:
            raise forms.ValidationError(
                f'You can withdraw at most Rs.{max_amount} '
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have Rs.{balance} in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount


class TransactionDateRangeForm(forms.Form):
    daterange = forms.CharField(required=False)

    def clean_daterange(self):
        daterange = self.cleaned_data.get("daterange")
        print(daterange)

        try:
            daterange = daterange.split(' - ')
            print(daterange)
            if len(daterange) == 2:
                for date in daterange:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                return daterange
            else:
                raise forms.ValidationError("Please select a date range.")
        except (ValueError, AttributeError):
            raise forms.ValidationError("Invalid date range")
