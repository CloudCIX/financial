# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.nominal_ledger_base import NominalLedgerBase


__all__ = [
    'ProfitAndLossListController',
]


class ProfitAndLossListController(NominalLedgerBase):
    """
    Validate User data used to specify which records will be used when listing Nominal Account totals for a Profit and
    Loss sheet
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this controller
        """
        validation_order = (
            'address_id',
            'start_date',
            'end_date',
        )

    error_codes = {
        'address_id__not_int': 'financial_profit_and_loss_list_101',
        'start_date__not_isoformat': 'financial_profit_and_loss_list_102',
        'end_date__not_isoformat': 'financial_profit_and_loss_list_103',
        'end_date__before_start_date': 'financial_profit_and_loss_list_104',
    }
