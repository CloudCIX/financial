# stdlib
from datetime import datetime
from decimal import Decimal
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
from django.db.models import Sum
from django.db.models.functions import Coalesce
# local
from financial.models import NominalLedger, NominalLedgerCredit, NominalLedgerDebit

__all__ = [
    'PeriodEndListController',
    'PeriodEndCreateController',
]


class PeriodEndListController(ControllerBase):
    """
    Validate User data to filter a list of Nominal Ledger records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'transaction_date',
            'narrative',
            'period_end_balance',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'narrative': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'period_end_balance': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'transaction_date': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class PeriodEndCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Ledger entry for a Period End transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'narrative',
            'transaction_date',
        )

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of why the Period End was created
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_period_end_create_101'

        self.cleaned_data['narrative'] = narrative
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date marking the end of a Financial Period
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d')
        except (TypeError, ValueError):
            return 'financial_period_end_create_102'

        if transaction_date > datetime.utcnow():
            return 'financial_period_end_create_103'

        period_end = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if period_end.exists():
            return 'financial_period_end_create_104'

        # Calculate the total debits and credits from the last period end up to `transaction_date`. They should always
        # be equal, otherwise something has gone wrong in the db
        previous_date = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
        ).order_by(
            '-transaction_date',
        ).values_list(
            'transaction_date',
            flat=True,
        ).first() or datetime.strptime('1900-01-01', '%Y-%m-%d')

        transaction_ids = (10000, 10001, 10002, 10003, 10004, 10005, 11000, 11001, 11002, 11003, 11004, 11005)
        filters = {
            'nominal_ledger__address_id': self.request.user.address['id'],
            'nominal_ledger__transaction_date__gt': previous_date,
            'nominal_ledger__transaction_date__lte': transaction_date,
            'nominal_ledger__transaction_type_id__in': transaction_ids,
        }

        debits = NominalLedgerDebit.objects.filter(**filters).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0')),
        )
        credits = NominalLedgerCredit.objects.filter(**filters).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0')),
        )
        if debits['total'] != credits['total']:
            return 'financial_period_end_create_105'

        self.cleaned_data['transaction_date'] = transaction_date
        self.cleaned_data['period_end_balance'] = debits['total'].quantize(Decimal('1.0000'))
        return None
