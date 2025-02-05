# libs
from cloudcix_rest.controllers import ControllerBase


__all__ = [
    'VIESListController',
]


class VIESListController(ControllerBase):
    """
    Validate User data to filter a list of Nominal Ledger Debit/Credit records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the fields in ControllerBase.Meta to make them more specific to this class
        """
        search_fields = {
            'nominal_ledger__transaction_date': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }
        allowed_ordering = (
            'address_id',
        )
