# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.nominal_ledger_base import NominalLedgerBase


__all__ = [
    'TrialBalanceListController',
]


class TrialBalanceListController(NominalLedgerBase):
    """
    Validate User data used to specify which records will be used when listing Nominal Account totals for a Trial
    Balance
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this controller
        """
        validation_order = (
            'address_id',
            'date',
        )

    error_codes = {
        'address_id__not_int': 'financial_trial_balance_list_101',
        'date__not_isoformat': 'financial_trial_balance_list_102',
    }
