# libs
from cloudcix_rest.controllers import ControllerBase


__all__ = [
    'SalesByTerritoryListController',
]


class SalesByTerritoryListController(ControllerBase):
    """
    Validate User data used to specify which records will be used when calculating Sales by Territory totals.
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        search_fields = {
            'transaction_date': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }
        allowed_ordering = (
            'id',
            'name',
        )
