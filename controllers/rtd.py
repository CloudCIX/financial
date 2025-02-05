# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.nominal_ledger_base import NominalLedgerBase


__all__ = [
    'RTDListController',
]


class RTDListController(NominalLedgerBase):
    """
    Validate User data to list Nominal Ledger data for an Return of Trading Details report
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        validation_order = (
            'start_date',
            'end_date',
        )

    error_codes = {
        'start_date__not_isoformat': 'financial_rtd_list_101',
        'end_date__not_isoformat': 'financial_rtd_list_102',
        'end_date__before_start_date': 'financial_rtd_list_103',
    }
