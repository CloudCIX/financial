# libs
from cloudcix_rest.controllers import ControllerBase


__all__ = [
    'NominalAccountHistoryListController',
]


class NominalAccountHistoryListController(ControllerBase):
    """
    Validates User data used to filter a list of Transactions made using a specific Nominal Account
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'transaction_date',
        )
        search_fields = {
            'transaction_date': ('gt', 'gte', 'lt', 'lte'),
        }
