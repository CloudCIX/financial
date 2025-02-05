# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.nominal_ledger_base import NominalLedgerBase


__all__ = [
    'BalanceSheetListController',
]


class BalanceSheetListController(NominalLedgerBase):
    """
    Validate User data used to specify which records will be used when listing Nominal Account totals for a Balance
    Sheet
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        validation_order = (
            'address_id',
            'date',
        )

    error_codes = {
        'address_id__not_int': 'financial_balance_sheet_list_101',
        'date__not_isoformat': 'financial_balance_sheet_list_102',
    }
