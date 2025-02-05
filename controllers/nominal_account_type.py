# libs
from cloudcix_rest.controllers import ControllerBase


__all__ = [
    'NominalAccountTypeListController',
]


class NominalAccountTypeListController(ControllerBase):
    """
    Validates User data used to filter a list of Nominal Account Type records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this controller
        """
        allowed_ordering = (
            'description',
            'min_account_number',
        )
        search_fields = {
            'description': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'min_account_number': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }
