# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.nominal_ledger_base import NominalLedgerBase


__all__ = [
    'VAT3ListController',
]


class VAT3ListController(NominalLedgerBase):
    """
    Validate User data used to specify which records will be used when calculating totals for a VAT 3 report
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this controller
        """
        validation_order = (
            'start_date',
            'end_date',
        )

    error_codes = {
        'start_date__not_isoformat': 'financial_vat3_list_101',
        'end_date__not_isoformat': 'financial_vat3_list_102',
        'end_date__before_start_date': 'financial_vat3_list_103',
    }
