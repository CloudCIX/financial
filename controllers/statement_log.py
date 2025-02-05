# libs
from cloudcix_rest.controllers import ControllerBase


__all__ = [
    'StatementLogListController',
]


class StatementLogListController(ControllerBase):
    """
    Validates User data to filter a list of Statement Log records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'created',
            'status',
        )
        search_fields = {
            'contra_address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'status': ('iexact', 'in'),
        }
