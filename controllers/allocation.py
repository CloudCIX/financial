# stdlib
from decimal import Decimal, InvalidOperation
from typing import cast, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial import reserved_accounts as reserved
from financial.models import Allocation, NominalLedger


__all__ = [
    'AllocationCreateController',
    'AllocationListController',
]

SALE_TRANSACTIONS = [11002, 11003, 11004, 11005]
PURCHASE_TRANSACTIONS = [10002, 10003, 10004, 10005]
TYPES_ALLOWED = SALE_TRANSACTIONS + PURCHASE_TRANSACTIONS


class AllocationListController(ControllerBase):
    """
    Validates User data to filter a list of Tax Rate records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'created',
            'id',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'details__nominal_ledger__contra_address_id': ('in', ),
            'details__nominal_ledger__transaction_type_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'details__nominal_ledger__tsn': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class AllocationCreateController(ControllerBase):
    """
    Validate User data to create an Allocation for a set of debits and credits
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = Allocation
        validation_order = (
            'allocations',
        )

    def validate_allocations(self, allocations: Optional[str]) -> Optional[str]:
        """
        description: A set of transactions to allocate debits and credits against each other
        type: array
        items:
            type: object
            properties:
                amount:
                    type: string
                    format: decimal
                tsn:
                    type: integer
                transaction_type_id:
                    type: integer
        """
        if not isinstance(allocations, list):
            return 'financial_allocation_create_101'
        if len(allocations) < 2:
            return 'financial_allocation_create_102'

        balance = Decimal('0')
        contra_address_id = 0
        sale = None

        for line in allocations:
            if not isinstance(line, dict):
                return 'financial_allocation_create_103'
            try:
                line['amount'] = Decimal(str(line['amount']))
            except (InvalidOperation, KeyError):
                return 'financial_allocation_create_104'
            try:
                tsn = int(cast(int, line['tsn']))
            except (TypeError, ValueError):
                return 'financial_allocation_create_105'
            try:
                transaction_type = int(cast(int, line['transaction_type_id']))
            except (TypeError, ValueError):
                return 'financial_allocation_create_106'
            if transaction_type not in TYPES_ALLOWED:
                return 'financial_allocation_create_107'
            if sale is None:
                # Is this allocations double entry to the Creditors Nominal Account or the Debtors Nominal Account
                sale = transaction_type in SALE_TRANSACTIONS
                nominal_account_number = reserved.DEBTOR_CONTROL_ACCOUNT if sale else reserved.CREDITOR_CONTROL_ACCOUNT
                self.cleaned_data['nominal_account_number'] = nominal_account_number
            if sale:
                if transaction_type not in SALE_TRANSACTIONS:
                    return 'financial_allocation_create_108'
            else:
                if transaction_type not in PURCHASE_TRANSACTIONS:
                    return 'financial_allocation_create_109'
            try:
                nominal_ledger = NominalLedger.objects.get(
                    tsn=tsn,
                    transaction_type_id=transaction_type,
                    address_id=self.request.user.address['id'],
                )
                line['nominal_ledger'] = nominal_ledger
            except NominalLedger.DoesNotExist:
                return 'financial_allocation_create_110'
            # All Nominal Ledger transaction have the same contra_address_id
            if contra_address_id == 0:
                contra_address_id = nominal_ledger.contra_address_id
            elif contra_address_id != nominal_ledger.contra_address_id:
                return 'financial_allocation_create_111'
            unallocated_balance = Decimal(str(nominal_ledger.unallocated_balance))
            if unallocated_balance > 0:
                if line['amount'] > 0:
                    return 'financial_allocation_create_112'
                if (line['amount'] * -1) > unallocated_balance:
                    return 'financial_allocation_create_113'
            elif unallocated_balance < 0:
                if line['amount'] < 0:
                    return 'financial_allocation_create_114'
                if (line['amount'] * -1) < unallocated_balance:
                    return 'financial_allocation_create_115'
            else:
                return 'financial_allocation_create_116'
            balance += line['amount']

        if balance != 0:
            return 'financial_allocation_create_117'

        self.cleaned_data['details'] = allocations

        return None
