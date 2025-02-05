# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.transactions_by_country_base import TransactionsByCountryBase


__all__ = [
    'PurchasesByCountryListController',
]


class PurchasesByCountryListController(TransactionsByCountryBase):
    """
    Validate User data used to specify which records will be used when calculating Purchases by Country totals.
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        validation_order = (
            'address_id',
            'start_date',
            'finish_date',
        )

    error_codes = {
        'address_id__not_int': 'financial_purchases_by_country_list_101',
        'start_date__not_isoformat': 'financial_purchases_by_country_list_102',
        'finish_date__not_isoformat': 'financial_purchases_by_country_list_103',
        'finish_date__before_start_date': 'financial_purchases_by_country_list_104',
    }
