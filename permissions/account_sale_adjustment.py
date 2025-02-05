# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from financial.models.nominal_ledger import NominalLedger


__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create an Account Sale Adjustment is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_account_sale_adjustment_create_201')

        return None

    @staticmethod
    def contra_create(request: Request) -> Optional[Http403]:
        """
        The request to create an Account Sale Adjustment Contra is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_account_sale_adjustment_contra_create_201')

        return None

    @staticmethod
    def contra_read(request: Request, obj: NominalLedger) -> Optional[Http403]:
        """
        The request to read an Account Sale Adjustment from another Address is valid if:
        - The Account Sale Adjustment's Contra Address is the same as the requesting User's Address
        """
        # The Account Sale Adjustment's Contra Address is the same as the requesting User's Address
        if obj.contra_address_id != request.user.address['id']:
            return Http403(error_code='financial_account_sale_adjustment_contra_read_201')

        return None
