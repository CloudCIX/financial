# libs
from cloudcix_rest.controllers import ControllerBase


__all__ = [
    'CreditorAccountListController',
]


class CreditorAccountListController(ControllerBase):
    """
    Validates User data to filter a list of Nominal Ledger records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'transaction_date',
            'transaction_type_id',
            'tsn',
        )
        search_fields = {
            'transaction_date': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'transaction_type_id': ('gt', 'gte', 'in', 'lt', 'lte'),
            'tsn': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }
