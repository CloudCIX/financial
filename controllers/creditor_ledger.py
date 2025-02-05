# stdlib
from typing import Dict
# libs
from cloudcix_rest.controllers import ControllerBase


__all__ = [
    'CreditorLedgerListController',
    'CreditorLedgerAgedListController',
    'CreditorLedgerTransactionListController',
    'CreditorLedgerContraTransactionListController',
]


class CreditorLedgerListController(ControllerBase):
    """
    Validate User data to filter a list of Nominal Ledger records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'balance',
        )
        search_fields = {
            'transaction_date': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class CreditorLedgerAgedListController(ControllerBase):
    """
    Validate User data to filter a list of Nominal Ledger records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'current_balance',
            'balance_30_day',
            'balance_60_day',
            'balance_90_day',
            'balance_120_day',
            'older_balance',
        )
        search_fields: Dict = dict()


class CreditorLedgerTransactionListController(ControllerBase):
    """
    Validate User data to filter a list of Nominal Ledger records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'contra_address_id',
            'transaction_date',
            'transaction_type_id',
            'tsn',
        )
        search_fields = {
            'contra_address_id': ('in', ),
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'transaction_date': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            # There's already a `transaction_type_id__range` in the filter of this controller's view, letting the User
            # add another range would raise an error
            'transaction_type_id': ('gt', 'gte', 'in', 'lt', 'lte'),
            'tsn': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class CreditorLedgerContraTransactionListController(ControllerBase):
    """
    Validate User data to filter a list of Nominal Ledger records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'transaction_date',
            'transaction_type_id',
            'tsn',
            'unallocated_balance',
        )
        search_fields = {
            'address_id': ('in', ),
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'transaction_date': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            # There's already a `transaction_type_id__range` in the filter of this controller's view, letting the User
            # add another range would raise an error
            'transaction_type_id': ('gt', 'gte', 'in', 'lt', 'lte'),
            'tsn': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'unallocated_balance': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }
