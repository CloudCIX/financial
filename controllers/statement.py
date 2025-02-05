# stdlib
from typing import cast, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.models.statement_settings import StatementSettings


__all__ = [
    'StatementCreateController',
]


class StatementCreateController(ControllerBase):
    """
    Validate User data to generate a Statement
    """

    class Meta(ControllerBase):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        # This controller does not create records in the DB
        model = None
        validation_order = (
            'address_id',
            'contra_address_id',
        )

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of an Address who the statement will be sent from. If not sent, the default will be the requesting
            users address.
        type: integer
        required: optional
        """
        if address_id is None:
            self.cleaned_data['address_id'] = self.request.user.address['id']
            return None

        try:
            address_id = int(cast(int, address_id))
        except (TypeError, ValueError):
            return 'financial_statement_create_101'

        if self.request.user.id != 1:
            # A user can only send statements from their own address
            if address_id != self.request.user.address['id']:
                return 'financial_statement_create_102'

        # Make sure the address_id has statement settings set up before continuing
        try:
            StatementSettings.objects.get(address_id=address_id)
        except StatementSettings.DoesNotExist:
            return 'financial_statement_create_103'

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_contra_address_id(self, contra_address_id: Optional[int]) -> Optional[str]:
        """
        description: The id of an Address who will be sent a statement.
        type: integer
        """
        if contra_address_id is None:
            return 'financial_statement_create_104'

        try:
            contra_address_id = int(cast(int, contra_address_id))
        except (TypeError, ValueError):
            return 'financial_statement_create_105'

        self.cleaned_data['contra_address_id'] = contra_address_id
        return None
