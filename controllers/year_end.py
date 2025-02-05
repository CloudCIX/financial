# stdlib
from datetime import datetime
from decimal import Decimal
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
from django.db.models import Sum
from django.db.models.functions import Coalesce
# local
from financial import reserved_accounts as reserved
from financial.models import NominalLedger, NominalLedgerCredit, NominalLedgerDebit


__all__ = [
    'YearEndListController',
    'YearEndCreateController',
]


class YearEndListController(ControllerBase):
    """
    Validate User data to filter a list of Nominal Ledger records that use the Year End Transaction Type
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the fields in ControllerBase.Meta to make them more specific to this class
        """
        allowed_ordering = (
            'transaction_date',
            'period_end_balance',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'narrative': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'period_end_balance': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'transaction_date': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class YearEndCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Ledger record for a Year End transaction
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
        description: A short description of the Year End transaction
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_year_end_create_101'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Year End was made
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d')
        except (TypeError, ValueError):
            return 'financial_year_end_create_102'

        # Make sure the transaction date is not in the future
        if transaction_date > datetime.utcnow():
            return 'financial_year_end_create_103'

        # Make sure the date has not been processed by a period end
        address_id = self.request.user.address['id']
        obj = NominalLedger.period_end.filter(
            address_id=address_id,
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_year_end_create_104'

        # Make sure the Suspense Account has been closed at this date. This account is for temporarily storing
        # transactions when there's uncertainty about which account they should be stored in
        debits = NominalLedgerDebit.objects.filter(
            nominal_account_number=reserved.SUSPENSE_ACCOUNT,
            nominal_ledger__address_id=address_id,
            nominal_ledger__transaction_date__lte=transaction_date,
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        credits = NominalLedgerCredit.objects.filter(
            nominal_account_number=reserved.SUSPENSE_ACCOUNT,
            nominal_ledger__address_id=address_id,
            nominal_ledger__transaction_date__lte=transaction_date,
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        if debits != credits:
            return 'financial_year_end_create_105'

        # Get the date of the previous Year End
        previous_year_end = NominalLedger.year_ends.filter(
            address_id=address_id,
        ).order_by(
            '-transaction_date',
        ).values_list(
            'transaction_date',
            flat=True,
        ).first() or datetime.strptime('1900-01-01', '%Y-%m-%d')

        # Calculate the Period End Balance for the Year End
        transaction_ids = (10000, 10001, 10002, 10003, 10004, 10005, 11000, 11001, 11002, 11003, 11004, 11005)
        filters = {
            'nominal_ledger__address_id': address_id,
            'nominal_ledger__transaction_date__gt': previous_year_end,
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
            # This should only ever fail if something went wrong in the db
            return 'financial_year_end_create_106'

        self.cleaned_data['previous_year_end'] = previous_year_end
        self.cleaned_data['period_end_balance'] = debits['total']
        self.cleaned_data['transaction_date'] = transaction_date
        return None
